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
    Dict,
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
    race: Optional[str]
    gender: Optional[str]
    description: List[str]
    eqs: List[str]
    cmds: List[str]


class State(NamedTuple):
    conn: Any
    sqlConnection: Any
    sqlCursor: Any
    room: Optional[str]
    area: Optional[str]
    areaId: Optional[int]
    monsters: Mapping[str, Monster]
    aggroStatus: Dict[str, bool]
    newMonstersInThisRoom: List[str]
    monstersInThisRoom: List[str]
    currentMobInfo: Optional[CurrentMobInfo]
    isDeadShortname: Optional[str]
    isDeadTimestamp: Optional[float]
    myLevel: Optional[int]
    mobInfoCommands: List[str]
    areaHasRooms: bool
    auto: bool


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
  m.race,
  m.gender,
  m.alignment,
  m.aggro,
  m.spells,
  m.skills,
  m.wikiexp,
  count(k.id) as killcount,
  ceil(percentile_disc(0.5) within group (order by k.exp) / 1000.0) as exp,
  m.room_id,
  m.area_id
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

MONSTER_ALIGNMENT_UPDATE = """UPDATE
  monster
SET
  alignment = %(alignment)s
WHERE
  id = %(monsterId)s
"""

MONSTER_MOBLOOK_UPDATE = """UPDATE
  monster
SET
  (shortname, gender, race, description, eqs, aggro) = (%(shortname)s, %(gender)s, %(race)s, %(description)s, %(eqs)s, %(aggro)s)
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

AREAID_INSERT = """INSERT INTO
  area
DEFAULT VALUES RETURNING id"""

AREANAME_INSERT = """INSERT INTO
  areaname (name, \"default\", wiki, batshoppe, area_id)
VALUES
  (%(area)s, 't', 'f', 'f', %(areaId)s)
"""

LEVEL_INSERT = """INSERT INTO
  monsterlvl (monster_id, ownlvl, consider, created)
VALUES
  (%(monsterId)s, %(ownlvl)s, %(consider)s, NOW())
"""

state = State(
    None,
    None,
    None,
    None,
    None,
    None,
    {},
    {},
    [],
    [],
    None,
    None,
    None,
    None,
    [],
    False,
    False,
)


def toggleAuto(s: str):
    global state
    state = state._replace(auto=not state.auto)
    tfprint("Automatic moblook: {0}".format(state.auto))


def loadArea(area: str):
    global state
    state.sqlCursor.execute(AREA_BY_NAME, {"area": area})
    areaId = state.sqlCursor.fetchone()
    if areaId is None:
        tfprint("Adding new area {0}".format(area))
        state.sqlCursor.execute(AREAID_INSERT)
        newAreaId = state.sqlCursor.fetchone()
        state.sqlCursor.execute(AREANAME_INSERT, {"areaId": newAreaId.id, "area": area})
        state.sqlConnection.commit()
        areaId = newAreaId

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
            monster.race,
            monster.gender,
            monster.alignment,
            monster.aggro,
            monster.spells,
            monster.skills,
            monster.killcount,
            monster.exp,
            monster.wikiexp,
            monster.room_id,
            monster.area_id,
        )

    state = state._replace(areaId=areaId.id, monsters=monsters)
    tfprint("Loaded {0} monsters for area {1}".format(len(monsters), area))


def addMonsterToRoom(name: str):
    global state
    # encircled, wrapped
    parsedName = name
    state.newMonstersInThisRoom.append(name)


def setMonsterAggro(name: str):
    global state
    state.aggroStatus[name] = True


def setMonsterUnaggro(name: str):
    global state
    state.aggroStatus[name] = False


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

    shortnames = []

    for name in state.monstersInThisRoom:
        indexAndMonster = monsterIndex(name)
        if indexAndMonster is not None:
            state.conn.send_bytes(dill.dumps(indexAndMonster))
            if name in state.monsters and state.monsters[name].shortname is not None:
                shortnames.append(state.monsters[name].shortname)
    if state.auto:
        doMoblook("")


def doMoblook(s: str):
    global state
    uniqCount = len(set(state.monstersInThisRoom))
    if uniqCount == 1:
        mi = monsterIndex(state.monstersInThisRoom[0])
        if mi is not None:
            [index, monster] = mi
            if monster.shortname is not None and (
                monster.race is None or monster.gender is None or monster.aggro is None
            ):
                moblook("{0} {1}".format(index + 1, monster.shortname))
            elif monster.shortname is None:
                tfprint("Monster not known, do a manual moblook")
            else:
                tfprint("{0} already in db".format(monster.shortname))
    elif uniqCount > 1:
        tfprint("More than one monster in the room, not supported")


def updateMonster(id: int, name: str):
    global state
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
            if m.areaId is None:
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


def whereami(s: str):
    global state
    area = s.lower()
    if state.area != area and area[-13:] != "(player city)" and area[-6:] != "(ship)":
        tfprint("Area changed to {0}".format(area))
        state.monstersInThisRoom.clear()
        state = state._replace(area=area)
        loadArea(area)


def whereamiMappedArea(s: str):
    global state
    area = s.lower()
    state = state._replace(areaHasRooms=False, room=None)
    if state.area is None or not state.area.startswith(area):
        tfeval("@whereami")


def room(s: str):
    global state
    [room, area] = textdecode(s).split(" ", 1)
    if area[-13:] == "(player city)" or area[-6:] == "(ship)":
        state.monstersInThisRoom.clear()
        state = state._replace(room=room, area=None, areaId=None, monsters={})
        return
    elif state.area != area:
        whereami(area)
    state = state._replace(room=room, areaHasRooms=True)
    roomDone()


def prompt(s: str):
    global state
    if state.areaHasRooms == False and len(state.newMonstersInThisRoom) > 0:
        roomDone()


def lookEnd(s: str):
    roomDone()


def roomDone():
    global state
    state = state._replace(
        monstersInThisRoom=state.newMonstersInThisRoom, newMonstersInThisRoom=[]
    )
    updateMonsters()
    monsterInfo()


def printState(s: str):
    global state
    tfprint(str(state._replace(monsters={})))


def isDead(shortname: str):
    global state
    # don't try to do shortname update from is dead message if the previous kill
    # was less that 2 seconds ago
    if state.isDeadTimestamp is None or time() - state.isDeadTimestamp > 2:
        state = state._replace(isDeadShortname=shortname, isDeadTimestamp=time())
    else:
        state = state._replace(isDeadShortname=None, isDeadTimestamp=None)


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
        # long names in p kills are shortened
        match = next(
            (match for match in state.monsters if match.startswith(name)), None
        )
        if match is not None:
            monster = state.monsters[match]
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


def gender(s: str):
    global state
    gender: Optional[str] = None

    if s == "He":
        gender = "m"
    elif s == "She":
        gender = "f"
    elif s == "It":
        gender = "n"
    else:
        tfprint("Unknown gender {0}".format(s))

    if state.currentMobInfo is not None and gender is not None:
        state = state._replace(
            currentMobInfo=state.currentMobInfo._replace(gender=gender)
        )

    tfeval("/edit -c0 mobinfo_desc")


def race(race: str):
    global state
    if state.currentMobInfo is not None:
        state = state._replace(currentMobInfo=state.currentMobInfo._replace(race=race))


def shortname(shortname: str):
    global state
    if state.currentMobInfo is not None:
        state = state._replace(
            currentMobInfo=state.currentMobInfo._replace(shortname=shortname)
        )
        tfeval("/edit -c100 mobinfo_desc")
        tfeval("/edit -c100 mobinfo_eqs_start")
        tfeval(
            "/edit -c100 -mregexp -t`"
            + "^spec_spell: {0} is an? \(.+\)\.`".format(shortname)
            + " mobinfo_race"
        )


def desc(s: str):
    global state
    if state.currentMobInfo is not None:
        state.currentMobInfo.description.append(s)


def eqs(s: str):
    global state
    if state.currentMobInfo is not None:
        state.currentMobInfo.eqs.append(s)


def eqsStart(s: str):
    global state
    if state.currentMobInfo is not None:
        tfeval("/edit -c0 mobinfo_desc")
        tfeval("/edit -c100 mobinfo_eqs")


def moblook(s: str):
    global state
    [i, name] = s.split(" ", 1)
    try:
        state = state._replace(
            currentMobInfo=CurrentMobInfo(
                int(i), None, None, None, [], [], deepcopy(state.mobInfoCommands)
            )
        )
        tfeval("@moblook {0}".format(name))
    except:
        tfprint(s)
        tfprint(i)
        tfprint(name)
        return


def moblookStart(s: str):
    tfeval("/edit -c100 mobinfo_scan")
    tfeval("/edit -c100 mobinfo_gender")


def moblookEnd(s: str):
    global state
    tfeval("/edit -c0 mobinfo_scan")
    tfeval("/edit -c0 mobinfo_gender")
    tfeval("/edit -c0 mobinfo_race")
    tfeval("/edit -c0 mobinfo_desc")
    tfeval("/edit -c0 mobinfo_eqs")
    tfeval("/edit -c0 mobinfo_eqs_start")

    if state.currentMobInfo is not None:
        monster = monsterFromIndex(state.currentMobInfo.i)
        shortname = state.currentMobInfo.shortname
        gender = state.currentMobInfo.gender
        race = state.currentMobInfo.race

        if race is None:
            tfprint("Monocle peer did not work, try again!")
        elif monster is not None:
            id = monster.id
            name = monster.name
            description: Optional[str] = None
            if len(state.currentMobInfo.description) > 0:
                description = "\n".join(state.currentMobInfo.description)
            eqs: Optional[str] = None
            if len(state.currentMobInfo.eqs) > 0:
                eqs = "\n".join(state.currentMobInfo.eqs)
            aggro = state.aggroStatus[monster.name]

            tfprint(
                "Updating monster {0} {1}: ({2}, {3}, {4}, {5})".format(
                    id, name, shortname, gender, race, aggro
                )
            )
            state.sqlCursor.execute(
                MONSTER_MOBLOOK_UPDATE,
                {
                    "monsterId": id,
                    "shortname": shortname,
                    "gender": gender,
                    "race": race,
                    "description": description,
                    "eqs": eqs,
                    "aggro": aggro,
                },
            )
            state.sqlConnection.commit()
            if state.area:
                loadArea(state.area)

            doNextMoblookCmd()


def doNextMoblookCmd():
    global state
    if state.currentMobInfo is None or len(state.currentMobInfo.cmds) == 0:
        return

    cmd = "@{0} {1};cast info".format(
        state.currentMobInfo.cmds.pop(0), state.currentMobInfo.shortname
    )
    tfeval(cmd)


def align(s: str):
    [shortname, align] = s.split("_", 1)
    tfeval("/edit -c0 mobinfo_align")

    if state.currentMobInfo is not None and state.currentMobInfo.shortname == shortname:
        monster = monsterFromIndex(state.currentMobInfo.i)
        if monster is not None:
            id = monster.id
            tfprint("Updating monster {0} {1}: ({2})".format(id, monster.name, align))
            state.sqlCursor.execute(
                MONSTER_ALIGNMENT_UPDATE,
                {"monsterId": id, "alignment": align},
            )
            state.sqlConnection.commit()
            if state.area:
                loadArea(state.area)
            doNextMoblookCmd()


def whoami(s: str):
    global state
    if s == "I":
        lvl = 101
    elif s == "II":
        lvl = 102
    elif s == "III":
        lvl = 103
    elif s == "IV":
        lvl = 104
    elif s == "V":
        lvl = 105
    else:
        lvl = int(s)
    state = state._replace(myLevel=lvl)


def levelStart(s: str):
    global state
    if state.currentMobInfo is not None and state.currentMobInfo.shortname == s:
        tfeval("/edit -c100 mobinfo_level")
    else:
        tfeval("/edit -c0 mobinfo_level")


def level(s: str):
    global state
    tfprint(s)
    tfeval("/edit -c0 mobinfo_level")
    if state.currentMobInfo is not None:
        monster = monsterFromIndex(state.currentMobInfo.i)
        if monster is not None:
            id = monster.id
            ownlvl = state.myLevel
            consider = s
            tfprint(
                "Updating monster {0} {1}: (level {2}: {3})".format(
                    id, monster.name, ownlvl, consider
                )
            )
            state.sqlCursor.execute(
                LEVEL_INSERT, {"monsterId": id, "consider": consider, "ownlvl": ownlvl}
            )
            state.sqlConnection.commit()
            doNextMoblookCmd()


def parseMobInfoCommands(s: str):
    global state
    cmds = s.split(";")
    tfprint(str(cmds))
    state = state._replace(mobInfoCommands=cmds)


def setup():
    global state

    conn = Client(MOBINFO_SOCKET_FILE, "AF_UNIX")
    sqlConnection = psycopg2.connect("dbname=batmud user=risto")
    sqlCursor = sqlConnection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    state = state._replace(conn=conn, sqlConnection=sqlConnection, sqlCursor=sqlCursor)

    cmds: Sequence[str] = [
        "/def -p10 -mglob -t`∴room *` "
        + "mobinfo_room = /python_call mobinfo.room \$[textencode({-1})]",
        "/def -p10 -F -mglob -t`* is DEAD, R.I.P.` "
        + "mobinfo_is_dead = /python_call mobinfo.isDead \%-L3",
        "/def -agGL -msimple -t`"
        + "Astounding!  You can see things no one else can see, such as pk_trigger_starts.`"
        + " party_kills_start = /python_call mobinfo.pkillsStart",
        "/def -agGL -msimple -t`"
        + "Astounding!  You can see things no one else can see, such as moblook_trigger_starts.`"
        + " mobinfo_moblook_start = /python_call mobinfo.moblookStart",
        "/def -agGL -msimple -t`"
        + "Astounding!  You can see things no one else can see, such as moblook_trigger_ends.`"
        + " mobinfo_moblook_end = /python_call mobinfo.moblookEnd",
        "/def -agGL -msimple -t`"
        + "Astounding!  You can see things no one else can see, such as look_ends.`"
        + " mobinfo_look_end = /python_call mobinfo.lookEnd",
        "/def -p10 -c0 -mregexp -t`"
        + "^([A-Za-z ,.'-]+) is (in (a )?)?(excellent shape|good shape|slightly hurt|noticeably hurt|not in a good shape|bad shape|very bad shape|near death) \\\(([0-9]+).\\\)\\\.\$`"
        + " mobinfo_scan = /python_call mobinfo.shortname \%P1",
        "/def -p10 -c0 -mregexp -t`"
        + "^\(He\|She\|It\) is (in (a )?)?(excellent shape|good shape|slightly hurt|noticeably hurt|not in a good shape|bad shape|very bad shape|near death)\\\.\$`"
        + " mobinfo_gender = /python_call mobinfo.gender \%P1",
        "/def -p10 -F -c0 -mregexp -t`Child is a (.+).`"
        + " mobinfo_race = /python_call mobinfo.race \%P1",
        "/def -p1 -F -c0 -mglob -t`*`"
        + " mobinfo_desc = /python_call mobinfo.desc \%*",
        "/def -p1 -F -c0 -mglob -t`*` mobinfo_eqs = /python_call mobinfo.eqs \%*",
        "/def -p10 -c0 -mglob -t`* equipment:`"
        + " mobinfo_eqs_start = /python_call mobinfo.eqsStart",
        "/def -p10 -mglob -t`You can almost see through *`"
        + " mobinfo_eqs_end_1 = /edit -c0 mobinfo_eqs",
        "/def -p10 -mglob -t`chan_say: You peer quizzically at *`"
        + " mobinfo_eqs_end_2 = /edit -c0 mobinfo_eqs",
        "/def -p10 -mglob -t`You don't see an exit *`"
        + " mobinfo_eqs_end_3 = /edit -c0 mobinfo_eqs",
        "/def -p11 -c0 -F -mregexp -t`"
        + "^spec_spell: ([A-Za-z ,.'-]+) is (evil|a bit evil|neutral|a bit good|good)\\\.\$`"
        + " mobinfo_align = /python_call mobinfo.align \%P1_\%P2",
        "/def -p10 -mglob -t`You are casting 'detect alignment' at *`"
        + " mobinfo_align_start = /edit -c100 mobinfo_align",
        "/def -p10 -F -mregexp -t`"
        + "^You are in '.+' in (.+) on the continent of .+. \\\(Coordinates: [0-9]+x, [0-9]+y; Global: [0-9]+x, [0-9]+y\\\)\$`"
        + " mobinfo_whereami = /python_call mobinfo.whereami \%P1",
        "/def -p10 -F -mregexp -t`"
        + "^You are in '.+', which is on the continent of .+\\\. \\\(Coordinates: [0-9]+x, [0-9]+y; Global: [0-9]+x, [0-9]+y\\\)\$`"
        + " mobinfo_whereami_outworld = /python_call mobinfo.whereami outworld",
        "/def -p10 -F -mregexp -t`"
        + "^[<.]---------[-^]---------[>.] +Loc: +(.+) \\\(.+\\\)?\$`"
        + " mobinfo_whereami_mapped_area = /python_call mobinfo.whereamiMappedArea \%P1",
        "/def -p10 -F -mregexp -t`"
        + "^[<.]---------[-^]---------[>.] +Loc: [^(]+ \\\[`"
        + " mobinfo_whereami_mapped_area_outworld = /python_call mobinfo.whereamiMappedArea outworld",
        # prompt must be matched from hook PROMPT
        "/def -p10 -F -mglob -h`PROMPT PROMPT:*` mobinfo_prompt = /python_call mobinfo.prompt",
        "/def -p10 -F -mregexp -t`"
        + "^You are .+, a level ([0-9IVX]+|)`"
        + " mobinfo_whoami_level = /python_call mobinfo.whoami \%P1",
        "/def -p10 -F -mregexp -t`"
        + "^spec_skill: You take a close look at (.+) in comparison to yourself.\$`"
        + " mobinfo_level_start = /python_call mobinfo.levelStart \%P1",
        "/def -p10 -c0 -F -mglob -t`"
        + "spec_skill: Level-wise, *`"
        + " mobinfo_level = /python_call mobinfo.level \%-2",
        "/def -p10 -F -mregexp -t`"
        + "^'mobinfo_commands' is an command-alias to '(.+)'\\\.\$`"
        + " mobinfo_commands = /python_call mobinfo.parseMobInfoCommands \%P1",
        "/def -p10 -mglob -t`Exited to map from *` " + "mobinfo_area_exit = @whereami",
        "@whoami",
        "@command mobinfo_commands",
    ]
    # this command is too difficult to get through tfeval as string
    tfeval("/load ~/bat/bcproxy-tf-scripts/mobinfo.tf")
    for cmd in cmds:
        tfprint(cmd)
        tfeval(cmd)

    tfprint("Loaded mobinfo.py")


setup()

# TODO
# - oma level, consider level
