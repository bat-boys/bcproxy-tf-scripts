from enum import Enum
from itertools import chain
from tf import eval  # type: ignore


def flatten(xs):
    return list(chain.from_iterable(xs))


def tfprint(s: str):
    for line in s.split("\n"):
        eval("/echo -p @{Crgb450}»@{n} " + line + "@{n}")


class NoValue(Enum):
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)
