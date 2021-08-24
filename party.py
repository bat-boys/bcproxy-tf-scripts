import dill  # type: ignore
from json import loads as loadJson
from itertools import groupby
from multiprocessing.connection import Client
from os import getuid
from re import sub as reSub
from time import sleep, time
from tf import eval as tfeval  # type: ignore
from typing import cast, FrozenSet, Mapping, NamedTuple, Optional, Sequence, Set

from partytypes import Member, MemberDataSource, Place, State
from tfutils import tfprint
from utils import NoValue, strtoi

SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-party".format(getuid())
CONN = Client(SOCKET_FILE, "AF_UNIX")


#: binds for targetting party members
#: the fourth column will be first in the output as well (partyoutput.getStatus)
PLACE_KEYBINDS: Sequence[Sequence[Optional[str]]] = [
    [],
    [None, "^[7", "^[8", "^[9", "^[6"],
    [None, "^[u", "^[i", "^[o", "^[y"],
    [None, "^[j", "^[k", "^[l", "^[h"],
    [None, "^[m", "^[,", "^[.", "^[n"],
]

#: Batclient party status update message (62) fields
PARTY_STATUS_UPDATE_FIELDS = [
    "player",
    "race",
    "gender",
    "level",
    "hp",
    "maxhp",
    "sp",
    "maxsp",
    "ep",
    "maxep",
    "party_name",
    "place_x",
    "place_y",
    "creator",
    "formation",
    "member",
    "entry",
    "following",
    "leader",
    "linkdead",
    "resting",
    "idle",
    "invisible",
    "dead",
    "stunned",
    "unconscious",
    "party_exp",
    "total_party_exp",
    "party_length_in_seconds",
    "party_creation_time",
]


def parseMessage(message) -> Member:
    """
    Parse incoming party update message

    :param message: message as a string with fields separated by spaces
    :returns: dictionary with fields and their respective values
              boolean and number fields are converted to respective
              python data types
    """
    d = dict(zip(PARTY_STATUS_UPDATE_FIELDS, message.split(" ")))

    x = strtoi(d["place_x"])
    y = strtoi(d["place_y"])
    place = None if x == None or y == None else Place(cast(int, x), cast(int, y))

    return Member(
        str(d["player"]),
        int(d["hp"]),
        int(d["maxhp"]),
        int(d["sp"]),
        int(d["maxsp"]),
        int(d["ep"]),
        int(d["maxep"]),
        place,
        bool(d["formation"] == "1"),
        bool(d["member"] == "1"),
        bool(d["entry"] == "1"),
        bool(d["following"] == "1"),
        bool(d["leader"] == "1"),
        bool(d["linkdead"] == "1"),
        bool(d["resting"] == "1"),
        bool(d["idle"] == "1"),
        bool(d["invisible"] == "1"),
        bool(d["dead"] == "1"),
        int(d["stunned"]),
        int(d["unconscious"]),
        None,
        time(),
        MemberDataSource.BCPROXY,
    )


def getMemberByName(name: str) -> Optional[Member]:
    global state
    for member in state.members:
        if member.name == name:
            return member
    return None


UNKNOWN_PLACES: Sequence[Place] = [
    Place(1, 4),
    Place(2, 4),
    Place(3, 4),
    Place(4, 4),
    Place(4, 1),
    Place(4, 2),
    Place(4, 3),
]

#: batclient messages will have out-of-formation places as 6,1 or something
VALID_PLACES: FrozenSet[Place] = frozenset(
    [
        Place(1, 1),
        Place(1, 2),
        Place(1, 3),
        Place(2, 1),
        Place(2, 2),
        Place(2, 3),
        Place(3, 1),
        Place(3, 2),
        Place(3, 3),
    ]
)


def calculatePlaces():
    global state

    noPlace: Set[Member] = set([])
    places: Mapping[Place, Member] = {}

    for member in state.members:
        # unknown place
        if member.place == None or member.place not in VALID_PLACES:
            noPlace.add(member)
            continue

        membersInThisPlaceUpdatedAt = map(
            lambda m: m.updatedAt,
            filter(lambda m: m.place == member.place, state.members),
        )

        # allMembersInThisPlaceFromBcproxy = True
        allMembersInThisPlaceFromBcproxy = (
            len(
                list(
                    filter(
                        lambda m: m.source == MemberDataSource.PSS
                        and m.place == member.place,
                        state.members,
                    )
                )
            )
            == 0
        )

        # PSS is the authoritiative source for member location as it includes
        # also the nergal minions and riftwalker entities
        #
        # for bcproxy-only, if this is the most recent update for this place,
        # set it here
        #
        # this also works if there is only one member for this place
        if member.source == MemberDataSource.PSS or (
            allMembersInThisPlaceFromBcproxy
            and member.updatedAt == max(membersInThisPlaceUpdatedAt)
        ):
            places[member.place] = member
        else:
            noPlace.add(member)

    # check if members with unknown place can be left to their previous place
    for member in noPlace.copy():
        if member.name in state.previousPlaces:
            prevPlace = state.previousPlaces[member.name]
            if prevPlace not in places:
                places[prevPlace] = member
                noPlace.remove(member)

    # store the previous places
    previousPlaces: Mapping[str, Place] = {}
    for (place, member) in places.items():
        previousPlaces[member.name] = place
    state = state._replace(previousPlaces=previousPlaces)

    # just sort the rest by name the unknown members and set to locations
    for (place, member) in zip(UNKNOWN_PLACES, sorted(noPlace, key=lambda m: m.name)):
        places[place] = member

    state = state._replace(places=places)


def sendState():
    global state
    CONN.send_bytes(dill.dumps(state))


def changeTargetName(name: str):
    global state
    tfeval("/trigger You are now target-healing {0}.".format(name))
    state = state._replace(target=name)
    sendState()


def changeTargetPlace(placeRaw: str):
    global state
    placeList = placeRaw.split()
    place = Place(int(placeList[0]), int(placeList[1]))
    if place in state.places:
        target = reSub(r"^[+]", "", state.places[place].name)
        state = state._replace(target=target)
        tfeval("/trigger You are now target-healing {0}.".format(target))
        sendState()


def pssStart(opts):
    tfeval("/edit -c100 party_pss")
    tfeval("/edit -c100 party_pss_end")


def pssEnd(opts):
    global state
    if state.pssHasMinions:
        state = state._replace(pssHasMinions=False)
    else:
        tfeval("/edit -c0 -ag party_pss")
        tfeval("/edit -c0 -ag party_pss_end")
        tfeval("/edit -ag party_pss_start")


def handleNewMember(newMember: Member):
    global state
    newMembers = set(
        [
            newMember if member.name == newMember.name else member
            for member in state.members
        ]
    )
    if newMember not in newMembers:
        newMembers.add(newMember)
    state = state._replace(members=frozenset(newMembers))
    calculatePlaces()
    sendState()


def triggerPartyMsg(msg: str):
    newMember = parseMessage(msg)
    handleNewMember(newMember)


def triggerPartyLeave(msg: str):
    global state
    member = msg.capitalize()
    toBeRemoved = None
    for m in state.members:
        if member == m.name:
            toBeRemoved = m
    if toBeRemoved:
        newMembers = set(state.members)
        newMembers.remove(toBeRemoved)
        state = state._replace(members=frozenset(newMembers))
        calculatePlaces()
        sendState()


def spepstringToInt(s: str) -> Optional[int]:
    if s == "full":
        return 100
    elif s == "V. high" or s == "VERY high":
        return 80
    elif s == "high":
        return 60
    elif s == "medium":
        return 40
    elif s == "low":
        return 20
    elif s == "very low" or "VERY low":
        return 10
    elif s == "negative":
        return 0
    else:
        return None


def manualPs(opts: str):
    tfeval("/edit -an party_pss")
    tfeval("/edit -an party_pss_start")
    tfeval("/edit -an party_pss_end")
    tfeval("@ps")


def pssParse(opts):
    global state
    d = loadJson(opts)
    d["idle"] = d["idle"] == "*"
    d["x"] = strtoi(d["x"])
    d["y"] = strtoi(d["y"])
    d["name"] = d["name"].strip()
    d["hp"] = strtoi(d["hp"])
    d["maxhp"] = strtoi(d["maxhp"])
    d["sp"] = strtoi(d["sp"])
    d["maxsp"] = strtoi(d["maxsp"])
    d["ep"] = strtoi(d["ep"])
    d["maxep"] = strtoi(d["maxep"])
    d["spepstring"] = d["spepstring"].strip()

    # get nergal minions sp and ep strings
    if d["sp"] == None and d["spepstring"] != "":
        spep = d["spepstring"].split("  ")
        d["sp"] = spepstringToInt(spep[0].strip())
        d["ep"] = spepstringToInt(spep[-1].strip())
        d["maxsp"] = 100
        d["maxep"] = 100

    newMember = pssJsonToMember(d)

    if newMember.name[:1] == "+" or state.manualMinions:
        state = state._replace(pssHasMinions=True)

    # leave invis to be handled by batclient messages
    if newMember.name != "Someone":
        handleNewMember(newMember)


def pssJsonToMember(j) -> Member:
    unc = 0
    if j["state"] == "unc":
        unc = 1
    elif j["state"][:4] == "unc|":
        unc = int(j["state"][-1:]) + 2

    stu = 0
    if j["state"] == "stu":
        stu = 1
    elif j["state"][:4] == "stu|":
        stu = int(j["state"][-1:])

    return Member(
        j["name"],
        j["hp"],
        j["maxhp"],
        j["sp"],
        j["maxsp"],
        j["ep"],
        j["maxep"],
        Place(j["x"], j["y"]),
        j["state"] == "form",
        j["state"] == "mbr",
        j["state"] == "ent",
        j["state"] == "fol",
        j["state"] == "ldr",
        j["state"] == "ld",
        j["state"] == "rest",
        j["idle"],
        j["name"] == "Someone",
        j["state"] == "dead",
        stu,
        unc,
        j["state"][:3] == "amb",
        time(),
        MemberDataSource.PSS,
    )


def ginfo(s: str):
    global state
    # we'll want front row to be first, so this is done in a bit difficult way
    names = list()
    places = state.places
    for y in [1, 2, 3]:
        for x in [1, 2, 3]:
            place = Place(x, y)
            if place in places:
                names.append(places[place].name)
    for place in UNKNOWN_PLACES:
        if place in places:
            names.append(places[place].name)
    tfeval("/python_call ginfo.partyReport {0}".format(" ".join(names)))


def toggleManualMinions(s: str):
    global state
    if state.manualMinions:
        tfprint("Manual minions disabled")
        state = state._replace(manualMinions=False)
    else:
        tfprint("Manual minions enabled")
        state = state._replace(manualMinions=True)


def setup():
    tfeval(
        "/def -mglob -agGL -p10 -q -t'∴party *' bcproxy_party = "
        + "/python_call party.triggerPartyMsg \%-1"
    )

    tfeval(
        "/def -mglob -agGL -p10 -q -t'∴partyleave *' bcproxy_partyleave = "
        + "/python_call party.triggerPartyLeave \%-1"
    )

    for x in range(1, 5):
        for y in range(1, 5):
            tfeval(
                "/def -i -q -b'{0}' = /python_call party.changeTargetPlace {1} {2}".format(
                    PLACE_KEYBINDS[y][x], x, y
                )
            )

    tfeval(
        "/def -i -ag -c0 -p20 -mregexp -t`"
        + "^\\\|(.)(([1-3?])\\\.([1-3?])  )?"  # idle, y, x
        + "([+]?[A-Za-z ]+)  "  # name {12}
        + "([a-z]+\\\|?[0-9]?)? +"  # state
        + "([0-9]+)\\\( *([0-9]+)\\\) +"  # hp / maxhp
        + "(([0-9]+)\\\( *([0-9]+)\\\) +"  # sp / maxsp
        + "([0-9]+)\\\( *([0-9]+)\\\)|.+) +"  # ep / maxep
        + "\\\| .+ \\\| .+ \\\|\$"  # level + exp
        + "` party_pss = /python_call party.pssParse "
        + '{ "idle": "\%P1", "y": "\%P3", "x": "\%P4", '
        + '"name": "\%P5", '
        + '"state": "\%P6", '
        + '"hp": "\%P7", "maxhp": "\%P8", '
        + '"spepstring": "\%P9", '
        + '"sp": "\%P10", "maxsp": "\%P11", '
        + '"ep": "\%P12", "maxep": "\%P13" }'
        + ""
    )
    tfeval(
        "/def -i -F -ag -p20 -msimple -t`"
        + ",-----------------------------------------------------------------------------."
        + "` party_pss_start = /python_call party.pssStart"
    )
    tfeval(
        "/def -i -F -ag -c0 -p20 -msimple -t`"
        + "\\\`-----------------------------------------------------------------------------'"
        + "` party_pss_end = /python_call party.pssEnd"
    )

    tfprint("Loaded party.py")


setup()
state = State(frozenset([]), {}, {}, None, False, False)
