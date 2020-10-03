import dill  # type: ignore
from multiprocessing.connection import Listener
from os import getuid
from typing import cast, NamedTuple, Optional, Tuple

from partytypes import Member, Place, State

SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-party".format(getuid())


class Color(NamedTuple):
    r: int
    g: int
    b: int


RED = Color(0xFF, 0, 0)
GREEN = Color(0, 0xFF, 0)
YELLOW = Color(0xFF, 0xFF, 0)
WHITE = Color(0xFF, 0xFF, 0xFF)
OUT_OF_FORMATION_COLOR = Color(204, 153, 255)


def colorize(s: str, color: Optional[Color]) -> str:
    if color != None:
        color = cast(Color, color)
        return "\033[38;2;{0};{1};{2}m{3}\033[0m".format(color.r, color.g, color.b, s)
    else:
        return s


def draw(s):
    print("\033c", end="")  # clear screen
    print(s)


def getMemberState(member: Member) -> Tuple[str, Optional[Color]]:
    """
    String and color for member state
    """
    # ambushed is missing as batmud gives that in pss but not in the party
    # status message for batclient
    if member.unconscious == 1:
        return ("unc", RED)
    if member.unconscious > 1:
        return ("unc|{0}".format(str(member.unconscious - 2)), RED)
    if member.stunned > 0:
        return ("stu|{0}".format(str(member.stunned)), RED)

    if member.linkdead:
        return ("ld", None)
    if member.dead:
        return ("dead", None)
    if member.resting:
        return ("rest", None)

    if member.invisible:
        return ("invis", None)
    if member.formation:
        return ("form", None)
    if member.member:
        return ("mbr", None)
    if member.entry:
        return ("", None)
    if member.following:
        return ("fol", None)
    if member.leader:
        return ("ldr", None)

    return ("unk", RED)


def nameColor(member: Member) -> Optional[Color]:
    if member.unconscious or member.stunned:
        return RED
    if member.member:
        return OUT_OF_FORMATION_COLOR
    if (
        member.linkdead
        or member.idle
        or member.formation
        or member.resting
        or member.dead
    ):
        return None
    return WHITE


def lines(state: State, place: Place) -> Tuple[str, str]:
    """
    For given member place, get the tf status line strings (two lines per member)

    <player name> <hp>/<hpmax> <hpdiff to max>
    <player state> <ep> <sp>/<spmax> <* if player is cast target>

    For example:
         Ruska  408/ 445  -37
      ldr  224 1404/1404

    :param member: member data
    :returns: Tuple of two strings for tf status lines
    """

    if place not in state.places:
        return ("                        ", "                        ")

    member = state.places[place]
    name = colorize("{0: >9}".format(member.name[:8]), nameColor(member))
    hp = colorize(
        "{0: >4}".format(member.hp),
        greenRedGradient(member.hp, member.maxhp, 200, 0.2),
    )
    maxhp = "{0: >4}".format(member.maxhp)
    hpdiff = colorize(
        "{0: >5}".format(member.hp - member.maxhp or ""), Color(0xEA, 0x22, 0x22)
    )
    memberStateTuple = getMemberState(member)
    memberState = colorize("{0: >5}".format(memberStateTuple[0]), memberStateTuple[1])
    memberIsTarget = (
        colorize("{0:4}".format("*"), YELLOW) if state.target == member.name else "    "
    )

    return (
        "{0} {1}/{2}{3}".format(
            name,
            hp,
            maxhp,
            hpdiff,
        ),
        "{0} {1: >3} {2: >4}/{3: >4} {4}".format(
            memberState,
            member.ep,
            member.sp,
            member.maxsp,
            memberIsTarget,
        ),
    )


def greenRedGradient(
    n: int, n_max: int, all_red_abs: int, all_red_ratio: float
) -> Color:
    all_red = max(all_red_abs, int(n_max * all_red_ratio + 0.5))

    if n < all_red:
        return RED
    if n >= n_max:
        return GREEN

    # http://stackoverflow.com/a/340245
    # green is 0 and red 1, so invert the ratio to get maximum to be green
    # also, bottom 10% is already handled, so reduce 10% of maximum from both
    n_ratio = 1 - ((n - all_red) / (n_max - all_red))
    r = int(255 * n_ratio + 0.5)
    g = int(255 * (1 - n_ratio) + 0.5)
    return Color(r, g, 0)


def getStatus(state: State) -> str:
    s = ""
    hasCol4 = Place(4, 1) in state.places
    for y in range(0, 4):
        col1 = lines(state, Place(1, y + 1))
        col2 = lines(state, Place(2, y + 1))
        col3 = lines(state, Place(3, y + 1))
        col4 = lines(state, Place(4, y + 1))

        s += "{0} {1} {2} {3}\n".format(col4[0], col1[0], col2[0], col3[0])
        s += "{0} {1} {2} {3}\n".format(col4[1], col1[1], col2[1], col3[1])
    return s


with Listener(SOCKET_FILE, "AF_UNIX") as listener:
    print("listening to connections on {0}".format(SOCKET_FILE))

    while True:
        with listener.accept() as conn:
            print("connection opened", listener.last_accepted)

            while True:
                try:
                    state = cast(State, dill.loads(conn.recv_bytes()))
                    status = getStatus(state)
                    draw(status)
                except EOFError:
                    print("connection closed")
                    break
