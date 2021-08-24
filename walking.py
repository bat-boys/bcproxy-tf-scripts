from tf import eval  # type: ignore
from typing import NamedTuple, Sequence

from tfutils import tfprint


class WalkBind(NamedTuple):
    key: str
    direction: str


WALK_BINDS: Sequence[WalkBind] = [
    WalkBind("^[7", "nw"),
    WalkBind("^[8", "n"),
    WalkBind("^[9", "ne"),
    WalkBind("^[u", "w"),
    WalkBind("^[i", "l"),
    WalkBind("^[o", "e"),
    WalkBind("^[j", "sw"),
    WalkBind("^[k", "s"),
    WalkBind("^[l", "se"),
]


def setup():
    for key, direction in WALK_BINDS:
        eval("/def -i -q -b'{0}' = @{1}".format(key, direction))
    tfprint("Loaded walking.py")


setup()
