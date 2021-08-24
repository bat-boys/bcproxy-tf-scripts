from typing import Any, cast, Deque, FrozenSet, NamedTuple, Optional, Sequence

from utils import NoValue


class Monster(NamedTuple):
    id: int
    name: str
    shortname: Optional[str]
    spells: FrozenSet[str]
    skills: FrozenSet[str]
    killcount: Optional[int]
    exp: Optional[str]
    room: Optional[str]


class State(NamedTuple):
    latestMonster: Optional[Monster]
