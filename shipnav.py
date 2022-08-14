# You are in '(main deck) Peilipallo' in Diskopallo (ship) on the continent of Laenor. (Coordinates: 312x, 365y; Global: 8504x, 8557y)

from re import findall
from tf import eval as tfeval  # type: ignore
from typing import Mapping, NamedTuple, Optional, Sequence

from tfutils import tfprint


class Loc(NamedTuple):
    x: int
    y: int


AREAS: Mapping[str, Loc] = {
    "secladin": Loc(577, 681),
    "hugoville": Loc(594, 467),
    "bigeaul": Loc(528, 429),
    "farmhouse": Loc(387, 528),
    "foxhunt": Loc(434, 522),
    "ivory-tower": Loc(508, 347),
    "arelium": Loc(365, 471),
}


class State(NamedTuple):
    x: Optional[int]
    y: Optional[int]


state = State(None, None)


def cruise(s: str):
    global state
    if s in AREAS:
        state = state._replace(x=AREAS[s].x, y=AREAS[s].y)
    else:
        tfprint(str(s.split(" ")))
        (x, y) = s.split(" ")
        x = findall("\d+", x)[0]
        y = findall("\d+", y)[0]
        state = state._replace(x=int(x), y=int(y))
    tfeval("/edit -c100 shipnav_whereami")
    tfeval("@whereami")


def cruiseStart(s: str):
    global state
    (x, y) = s.split(" ")
    if state.x is not None and state.y is not None:
        xCount = state.x - int(x)
        yCount = state.y - int(y) + 1
        xDir = "e"
        yDir = "s"

        if xCount < 0:
            xCount = xCount * -1
            xDir = "w"
        if yCount < 0:
            yCount = yCount * -1
            yDir = "n"

        # go diagonally as far as we can, and the rest straight

        diagonalDir = yDir + xDir
        if xCount > yCount:
            diagonalCount = yCount
            straightCount = xCount - yCount
            straightDir = xDir
        else:
            diagonalCount = xCount
            straightCount = yCount - xCount
            straightDir = yDir

        cruisecmd = "cruise {0} {1},{2} {3}".format(
            diagonalCount, diagonalDir, straightCount, straightDir
        )

        tfprint(cruisecmd)
        tfeval("@gangway raise;ship launch;{0}".format(cruisecmd))
        tfeval("/edit -c0 shipnav_whereami")


def setup():
    tfeval(
        "/def -i -F -ag -p10 -c100 -mregexp "
        + "-t`^You are in '.main deck. Peilipallo' in Diskopallo .ship. on the continent of .+ .Coordinates: ([0-9]+)x, ([0-9]+)y.+` "
        + "shipnav_whereami = /python_call shipnav.cruiseStart \%P1 \%P2"
    )

    tfprint("Loaded shipnav.py")


setup()
