from collections import deque  # type: ignore
import dill  # type: ignore
from multiprocessing.connection import Listener
from os import getuid
from threading import Timer
from typing import cast, Tuple

from utils import Color, colorize, GREEN, RED, YELLOW, WHITE

MOBINFO_SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-mobinfo".format(getuid())

from mobinfotypes import Monster, State


def receiveMessage(msg: Tuple[int, Monster]):
    global state
    (index, monster) = msg
    if state.latestMonster != monster:
        mobnameColor = WHITE
        if (
            monster.shortname is None
            or monster.race is None
            or monster.gender is None
            or monster.align is None
        ):
            mobnameColor = Color(0xFF, 0xFF, 0xA0)
        print(colorize("{0} {1}".format(index + 1, monster.name[:35]), mobnameColor))

        exp = "?"
        if monster.exp is not None:
            expColor = GREEN
            if monster.exp is not None and monster.exp >= 50 and monster.exp < 150:
                expColor = YELLOW
            elif monster.exp is not None and monster.exp >= 150:
                expColor = RED
            exp = colorize(str(monster.exp), expColor)
        elif monster.wikiexp is not None:
            exp = monster.wikiexp

        print(
            "{0}/{1} {2} {3} {4} {5}".format(
                exp,
                monster.killcount,
                monster.shortname,
                monster.race,
                monster.gender,
                monster.align,
            )
        )
        spells = list(monster.spells) if monster.spells is not None else []
        skills = list(monster.skills) if monster.skills is not None else []
        spellsskills = spells + skills

        if len(spellsskills) > 0:
            print("   " + ", ".join(spellsskills))
        state = state._replace(latestMonster=monster)


state = State(None)

with Listener(MOBINFO_SOCKET_FILE, "AF_UNIX") as listener:
    print("listening to connections on {0}".format(MOBINFO_SOCKET_FILE))

    while True:
        with listener.accept() as conn:
            print("connection opened", listener.last_accepted)

            while True:
                try:
                    msg = cast(Tuple[int, Monster], dill.loads(conn.recv_bytes()))
                    receiveMessage(msg)
                except EOFError:
                    print("connection closed")
                    break
