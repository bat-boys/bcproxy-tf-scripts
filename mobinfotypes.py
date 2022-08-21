from typing import Any, cast, Deque, FrozenSet, NamedTuple, Optional, Sequence

from utils import NoValue


class Monster(NamedTuple):
    id: int
    name: str
    shortname: Optional[str]
    race: Optional[str]
    gender: Optional[str]
    align: Optional[str]
    aggro: Optional[bool]
    spells: FrozenSet[str]
    skills: FrozenSet[str]
    killcount: Optional[int]
    exp: Optional[float]
    wikiexp: Optional[str]
    room: Optional[str]
    areaId: Optional[str]


class State(NamedTuple):
    latestMonster: Optional[Monster]
