from typing import FrozenSet, Mapping, NamedTuple, Optional
from utils import NoValue


class Place(NamedTuple):
    x: int
    y: int


class MemberDataSource(NoValue):
    PSS = "pss"
    BCPROXY = "bcproxy"


class Member(NamedTuple):
    name: str
    hp: int
    maxhp: int
    sp: int
    maxsp: int
    ep: int
    maxep: int
    place: Optional[Place]
    formation: bool
    member: bool
    entry: bool
    following: bool
    leader: bool
    linkdead: bool
    resting: bool
    idle: bool
    invisible: bool
    dead: bool
    stunned: int
    unconscious: int
    ambushed: Optional[bool]
    updatedAt: float
    source: MemberDataSource


class State(NamedTuple):
    members: FrozenSet[Member]
    places: Mapping[Place, Member]
    previousPlaces: Mapping[str, Place]  # str is member.name
    target: Optional[str]
    pssHasMinions: bool
