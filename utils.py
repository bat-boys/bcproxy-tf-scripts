from enum import Enum
from itertools import chain
from typing import cast, NamedTuple, Optional, Sequence, TypeVar
from re import compile as reCompile

#: generic type variable, usage example in filterOutNones
T = TypeVar("T")


class Color(NamedTuple):
    r: int
    g: int
    b: int


def colorize(s: str, color: Optional[Color]) -> str:
    if color != None:
        color = cast(Color, color)
        return "\033[38;2;{0};{1};{2}m{3}\033[0m".format(color.r, color.g, color.b, s)
    else:
        return s


def flatten(xs):
    return list(chain.from_iterable(xs))


class NoValue(Enum):
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


def strtoi(s: str) -> Optional[int]:
    try:
        return int(s)
    except ValueError as e:
        return None


def filterOutNones(xs: Sequence[Optional[T]]) -> Sequence[T]:
    return cast(Sequence[T], filter(lambda x: x is not None, xs))


TEXTDECODE_RE = reCompile(r"^(.*)_([0-9]+)_(.*)$")


def textdecode(s: str) -> str:
    while True:
        match = TEXTDECODE_RE.match(s)
        if match is None:
            break
        [begin, char, end] = match.groups()
        s = begin + chr(int(char)) + end
    return s
