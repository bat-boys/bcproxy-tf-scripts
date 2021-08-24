from copy import deepcopy
import dill  # type: ignore
from multiprocessing.connection import Client
from os import getuid
import psycopg2  # type: ignore
import psycopg2.extras  # type: ignore
from time import time
from tf import eval as tfeval  # type: ignore
from typing import (
    Any,
    FrozenSet,
    List,
    Mapping,
    MutableMapping,
    MutableSequence,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from mobinfotypes import Monster
from tfutils import tfprint
from utils import textdecode


class CurrentMobInfo(NamedTuple):
    i: int
    shortname: Optional[str]


class State(NamedTuple):
    conn: Any
    sqlConnection: Any
    sqlCursor: Any
    room: Optional[str]
    area: Optional[str]
    areaId: Optional[int]
    monsters: Mapping[str, Monster]
    monstersInThisRoom: List[str]
    monstersInPrevRoom: List[str]
    currentMobInfo: Optional[CurrentMobInfo]
    currentLookLines: List[str]
    isDeadShortname: Optional[str]
    isDeadTimestamp: Optional[float]


MOBINFO_SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-mobinfo".format(getuid())


AREA_BY_NAME = """SELECT
  a.id
FROM
  area as a
  INNER JOIN areaname AS an ON a.id = an.area_id
WHERE
  an.name ILIKE %(area)s
"""

MONSTERS_BY_AREA = """SELECT
  m.id,
  m.name,
  m.shortname,
  m.spells,
  m.skills,
  m.wikiexp,
  count(k.id) as killcount,
  ceil(percentile_disc(0.5) within group (order by k.exp) / 1000.0) as exp,
  m.room_id
FROM
  monster AS m
  LEFT JOIN kill AS k ON k.monster_id = m.id
WHERE
  m.area_id = %(areaId)s
GROUP BY
  m.id
"""

MONSTER_ID_BY_NAME = """SELECT
  id
FROM
  monster
WHERE
  (name ILIKE %(name)s OR name ILIKE %(nameUndead)s) AND room_id IS NULL
"""

MONSTER_INSERT = """INSERT INTO
  monster (name, area_id, room_id, created)
VALUES
  (%(name)s, %(areaId)s, %(roomId)s, NOW())
"""

MONSTER_AREA_UPDATE = """UPDATE
  monster
SET
  (name, area_id, room_id) = (%(name)s, %(areaId)s, %(roomId)s)
WHERE
  id = %(monsterId)s
"""

MONSTER_SHORTNAME_UPDATE = """UPDATE
  monster
SET
  shortname = %(shortname)s
WHERE
  id = %(monsterId)s
"""

KILL_SELECT = """SELECT
  1
FROM
  kill
WHERE
  monster_id = %(monsterId)s
  AND exp = %(exp)s
  AND created >= NOW() - interval '1 day'
"""

KILL_INSERT = """INSERT INTO
  kill (monster_id, exp, created)
VALUES
  (%(monsterId)s, %(exp)s, NOW())
"""

state = State(None, None, None, None, None, None, {}, [], [], None, [], None, None)


def loadArea(area: str):
    global state
    state.sqlCursor.execute(AREA_BY_NAME, {"area": area})
    areaId = state.sqlCursor.fetchone()
    if areaId is None:
        tfprint("Area not found in database: {0}".format(area))
        return

    state.sqlCursor.execute(MONSTERS_BY_AREA, {"areaId": areaId.id})
    monsters = {}
    while True:
        monster = state.sqlCursor.fetchone()
        if monster is None:
            break
        monsters[monster.name] = Monster(
            monster.id,
            monster.name,
            monster.shortname,
            monster.spells,
            monster.skills,
            monster.killcount,
            monster.wikiexp if monster.killcount == 0 else "{0}k".format(monster.exp),
            monster.room_id,
        )

    state = state._replace(areaId=areaId.id, area=area, monsters=monsters)
    tfprint("Loaded {0} monsters for area {1}".format(len(monsters), area))


def addMonsterToRoom(name: str):
    global state
    state.monstersInThisRoom.append(name)


def monsterIndex(name: str) -> Optional[Tuple[int, Monster]]:
    global state
    if name in state.monsters:
        return (sorted(state.monsters.keys()).index(name), state.monsters[name])
    else:
        return None


def monsterFromIndex(i: int) -> Optional[Monster]:
    global state
    try:
        return state.monsters[sorted(state.monsters.keys())[i - 1]]
    except:
        return None


def monsterInfo():
    global state
    for name in state.monstersInThisRoom:
        indexAndMonster = monsterIndex(name)
        if indexAndMonster is not None:
            state.conn.send_bytes(dill.dumps(indexAndMonster))
    state.monstersInThisRoom.clear()


def updateMonster(id: int, name: str):
    global state
    # monster not found from area, let's check if it's in db without area
    if state.areaId is not None and state.area is not None:
        tfprint(
            "Updating monster {0} {1} to area {2} {3}".format(
                id, name, state.areaId, state.area
            )
        )
        state.sqlCursor.execute(
            MONSTER_AREA_UPDATE,
            {
                "areaId": state.areaId,
                "monsterId": id,
                "name": name,
                "roomId": state.room,
            },
        )
        state.sqlConnection.commit()
        loadArea(state.area)


def insertMonster(name: str):
    global state
    # monster not found from area, let's check if it's in db without area
    if state.areaId is not None and state.area is not None:
        tfprint(
            "Adding monster {0} to area {1} {2}".format(name, state.areaId, state.area)
        )
        state.sqlCursor.execute(
            MONSTER_INSERT,
            {
                "areaId": state.areaId,
                "name": name,
                "roomId": state.room,
            },
        )
        state.sqlConnection.commit()
        loadArea(state.area)


def updateMonsters():
    global state
    ms = deepcopy(state.monstersInThisRoom)
    while len(ms) > 0 and state.area is not None:
        name = ms.pop()
        if name in state.monsters:
            m = state.monsters[name]
            if m.room is None:
                updateMonster(m.id, m.name)
        else:
            state.sqlCursor.execute(
                MONSTER_ID_BY_NAME, {"name": name, "nameUndead": name + " (undead)"}
            )
            monsterId = state.sqlCursor.fetchone()
            if monsterId is not None:
                updateMonster(monsterId.id, name)
            else:
                insertMonster(name)


def room(s: str):
    global state
    [room, area] = textdecode(s).split(" ", 1)
    if area[-13:] == "(player city)" or area[-6:] == "(ship)":
        state.monstersInThisRoom.clear()
        state = state._replace(room=room, area=None, areaId=None, monsters={})
        return
    elif state.area != area:
        state.monstersInThisRoom.clear()
        loadArea(area)
    state = state._replace(
        room=room, area=area, monstersInPrevRoom=deepcopy(state.monstersInThisRoom)
    )
    updateMonsters()
    monsterInfo()


def printState(s: str):
    global state
    tfprint(str(state))


def end(s: str):
    global state
    if state.currentMobInfo is None:
        return

    monster = monsterFromIndex(state.currentMobInfo.i)
    if monster is not None:
        id = monster.id
        name = monster.name
        shortname = state.currentMobInfo.shortname
        tfprint("Updating monster {0} {1} shortname to {2}".format(id, name, shortname))
        state.sqlCursor.execute(
            MONSTER_SHORTNAME_UPDATE,
            {"monsterId": id, "shortname": shortname},
        )
        state.sqlConnection.commit()
    state = state._replace(currentMobInfo=None, currentLookLines=[])


def shortname(s: str):
    global state
    shortname = s[37:][:-27]
    if state.currentMobInfo is not None:
        state = state._replace(
            currentMobInfo=state.currentMobInfo._replace(shortname=shortname)
        )
        end("")


def isDead(shortname: str):
    global state
    # don't try to do shortname update from is dead message if the previous kill
    # was less that 2 seconds ago
    if state.isDeadTimestamp is None or time() - state.isDeadTimestamp > 2:
        state = state._replace(isDeadShortname=shortname, isDeadTimestamp=time())
    else:
        state = state._replace(isDeadShortname=None, isDeadTimestamp=None)


def cons(s: str):
    global state
    [i, name] = s.split(" ", 1)
    try:
        state = state._replace(currentMobInfo=CurrentMobInfo(int(i), None))
        tfeval("@consider {0}".format(name))
    except:
        tfprint(s)
        tfprint(i)
        tfprint(name)
        return


def pkillsStart(s: str):
    cmds = [
        "/def -agGL -mregexp -t`^\\\| [0-9]{1,2}:[0-9]{2}\\\s+[0-9]+: .+\\\|\$` "
        + "party_kills_line = /python_call mobinfo.updateExp \%*",
        "/def -agGL -mregexp -n1 -t`^This party has killed \\\d+ monsters? \\\(avg exp/mon: \\\d+\\\)\\\.\$` "
        + "party_kills_end = /undef party_kills_line",
        "@party kills 1",
    ]
    for cmd in cmds:
        tfeval(cmd)


def updateExp(s: str):
    global state
    s = s.strip("| ")
    s = s.rstrip("| \n")
    s = s[5:]  # remove timestamp
    parts = s.split(": ", 1)
    try:
        exp = int(parts[0])
        name = parts[1]
        if name in state.monsters:
            monster = state.monsters[name]
            state.sqlCursor.execute(KILL_SELECT, {"monsterId": monster.id, "exp": exp})
            killExists = state.sqlCursor.fetchone()
            if killExists is None:
                state.sqlCursor.execute(
                    KILL_INSERT, {"monsterId": monster.id, "exp": exp}
                )
                state.sqlConnection.commit()
                tfprint(
                    "Kill added: {0} {1}, {2} exp".format(monster.id, monster.name, exp)
                )
            if monster.shortname is None and state.isDeadShortname is not None:
                tfprint(
                    "Updating monster {0} {1} shortname to {2}".format(
                        monster.id, name, state.isDeadShortname
                    )
                )
                state.sqlCursor.execute(
                    MONSTER_SHORTNAME_UPDATE,
                    {"monsterId": monster.id, "shortname": state.isDeadShortname},
                )
                state = state._replace(isDeadShortname=None, isDeadTimestamp=None)
                state.sqlConnection.commit()
    except (ValueError, IndexError):
        # tf.err("error parsing kill line")
        return 1


def setup():
    global state

    conn = Client(MOBINFO_SOCKET_FILE, "AF_UNIX")
    sqlConnection = psycopg2.connect("dbname=batmud user=risto")
    sqlCursor = sqlConnection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    state = state._replace(conn=conn, sqlConnection=sqlConnection, sqlCursor=sqlCursor)

    cmds: Sequence[str] = [
        "/def -p10 -mglob -t`∴room *` "
        + "mobinfo_room = /python_call mobinfo.room \$[textencode({-1})]",
        "/def -p10 -F -mglob -t`"
        + "spec_skill: You take a close look at * in comparison to yourself."
        + "` mobinfo_shortname = /python_call mobinfo.shortname \%*",
        "/def -p10 -F -mglob -t`* is DEAD, R.I.P.` "
        + "mobinfo_is_dead = /python_call mobinfo.isDead \%-L3",
        "/def -agGL -msimple -t`"
        + "Astounding!  You can see things no one else can see, such as pk_trigger_starts.`"
        + " party_kills_start = /python_call mobinfo.pkillsStart",
    ]
    # this command is too difficult to get through tfeval as string
    tfeval("/load ~/bat/bcproxy-tf-scripts/mobinfo.tf")
    for cmd in cmds:
        tfprint(cmd)
        tfeval(cmd)

    tfprint("Loaded mobinfo.py")


setup()
