import dill  # type: ignore
from itertools import groupby
from multiprocessing.connection import Client
from os import getuid
from time import time
from tf import eval  # type: ignore
from typing import cast, FrozenSet, Mapping, NamedTuple, Optional, Sequence, Set

from partytypes import Member, Place, State
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
    )


def triggerPartyMsg(msg: str):
    global state
    newMember = parseMessage(msg)
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

#: bcproxy
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

        # if this is the most recent update for this place, set it here
        # this also works if there is only one member for this place
        if member.updatedAt == max(membersInThisPlaceUpdatedAt):
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
    eval("/trigger You are now target-healing {0}.".format(name))
    state = state._replace(target=name)


def changeTargetPlace(placeRaw: str):
    global state
    placeList = placeRaw.split()
    place = Place(int(placeList[0]), int(placeList[1]))
    if place in state.places:
        eval(
            "/trigger You are now target-healing {0}.".format(state.places[place].name)
        )
        state = state._replace(target=state.places[place].name)


def setup():
    eval(
        "/def -mglob -agGL -q -t'∴party *' bcproxy_party = "
        + "/python_call party.triggerPartyMsg \%-1"
    )
    eval("/def t = /python_call party.changeTargetName \%1")
    for x in range(1, 5):
        for y in range(1, 5):
            eval(
                "/def -i -q -b'{0}' = /python_call party.changeTargetPlace {1} {2}".format(
                    PLACE_KEYBINDS[y][x], x, y
                )
            )
    tfprint("Loaded party.py")


setup()
state = State(frozenset([]), {}, {}, None)
