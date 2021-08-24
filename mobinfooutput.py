from collections import deque  # type: ignore
import dill  # type: ignore
from multiprocessing.connection import Listener
from os import getuid
from threading import Timer
from typing import cast, Tuple

from utils import colorize

MOBINFO_SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-mobinfo".format(getuid())

from mobinfotypes import Monster, State


def receiveMessage(msg: Tuple[int, Monster]):
    global state
    (index, monster) = msg
    if state.latestMonster != monster:
        print(
            "{0}{1} {2}, {3}/{4}".format(
                index + 1,
                "*" if monster.shortname is None else ":",
                monster.name[:30],
                monster.exp if monster.exp is not None else "?",
                monster.killcount,
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
