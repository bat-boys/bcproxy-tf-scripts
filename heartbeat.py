import dill  # type: ignore
from multiprocessing.connection import Client
from os import getuid
from tf import eval as tfeval  # type: ignore
from typing import (
    FrozenSet,
    Mapping,
    MutableMapping,
    MutableSequence,
    NamedTuple,
    Optional,
    Sequence,
)

from spells import DamType, getSpellByName, Spell
from statustypes import Message, StatusType
from tfutils import tfprint

STATUS_SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-status".format(getuid())


def heartbeat(opts: str):
    with Client(STATUS_SOCKET_FILE, "AF_UNIX") as conn:
        msg = Message(StatusType.HEARTBEAT_RESET, None)
        conn.send_bytes(dill.dumps(msg))


def tick(spdiffRaw: str):
    try:
        spdiff = int(spdiffRaw)
        if spdiff > 120:
            with Client(STATUS_SOCKET_FILE, "AF_UNIX") as conn:
                msg = Message(StatusType.TICK_RESET, None)
                conn.send_bytes(dill.dumps(msg))
    except ValueError as e:
        None


def setup():
    cmds: Sequence[str] = [
        "/def -i -agGL -p10 -msimple -t`Dunk dunk` heartbeat = /python_call heartbeat.heartbeat",
        "/def -i -F -p10 -mregexp -t`"
        + "^H:(-?[0-9]+)/(-?[0-9]+) \\\[([+-]?[0-9]*)\\\] "
        + "S:(-?[0-9]+)/(-?[0-9]+) \\\[([+-]?[0-9]*)\\\] "
        + "E:(-?[0-9]+)/(-?[0-9]+) \\\[([+-]?[0-9]*)\\\] "
        + "\\\\\$:(-?[0-9]+) \\\[[+-]?[0-9]*\\\] "
        + "exp:(-?[0-9]+) \\\[[+-]?[0-9]*\\\]\$"
        + "` sc_update = /python_call heartbeat.tick \%P6",
    ]

    for cmd in cmds:
        tfprint(cmd)
        tfeval(cmd)

    tfprint("Loaded heartbeat.py")


setup()
