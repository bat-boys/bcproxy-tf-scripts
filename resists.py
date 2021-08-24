import dill  # type: ignore
from enum import Enum
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

from spells import DamType, getDamtypeColor, getSpellByName, Spell
from statustypes import Message, StatusType
from tfutils import tfprint
from utils import colorize

STATUS_SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-status".format(getuid())


class Resist(Enum):
    SCREAM = 0
    WRITHE = 20
    SHUDDER = 40
    GRUNT = 60
    WINCE = 80
    SHRUG = 100


class MobResist(NamedTuple):
    name: str
    resists: MutableMapping[DamType, Resist]


class State(NamedTuple):
    previousMob: Optional[str]
    previousSpell: Optional[Spell]
    previousDead: bool
    mobs: MutableSequence[MobResist]


def hits(mobAndSpell: str):
    global state
    splitted = mobAndSpell.split(" hits ")
    if len(splitted) == 2:
        spellname = splitted[0]
        mobname = splitted[1].strip(".")
        spell = getSpellByName(spellname)
        if spell is not None:
            state = state._replace(previousMob=mobname, previousSpell=spell)
            tfeval("/edit -c100 resist_scream")
            tfeval("/edit -c100 resist_writhe")
            tfeval("/edit -c100 resist_shudder")
            tfeval("/edit -c100 resist_grunt")
            tfeval("/edit -c100 resist_wince")
            tfeval("/edit -c100 resist_shrug")
    else:
        tfprint("Unknown resist string: {0}".format(mobAndSpell))


def report(mobResist: MobResist):
    # sort resists from smallest to largest
    rs = sorted(list(mobResist.resists.items()), key=lambda x: x[1].value)
    tfeval(
        "@party report {0} resists {1}".format(
            mobResist.name,
            ", ".join(map(lambda r: "{0} {1}%".format(r[0].value, r[1].value), rs)),
        )
    )

    with Client(STATUS_SOCKET_FILE, "AF_UNIX") as conn:
        msg = Message(
            StatusType.RESISTS,
            "{0} {1}".format(
                mobResist.name,
                ", ".join(
                    map(
                        lambda r: "{0}: {1}".format(
                            colorize(r[0].value[:4], getDamtypeColor(r[0])), r[1].value
                        ),
                        rs,
                    )
                ),
            ),
        )
        conn.send_bytes(dill.dumps(msg))


def reportLast(args):
    global state
    if len(state.mobs) > 0:
        report(state.mobs[0])


def resists(resist: Resist, mobnameRaw: str):
    global state
    resists: MutableMapping[DamType, Resist] = {}
    mobname = mobnameRaw[12:]  # raw has "spec_spell: " in the beginning

    if (
        state.previousSpell is not None
        and state.previousSpell.damType is not None
        and state.previousMob is not None
        and state.previousMob == mobname
    ):
        if state.previousDead == False and state.mobs[0].name == mobname:
            # this mob was shot already previously
            resists = state.mobs[0].resists
            damType = state.previousSpell.damType

            # new damtype, or changed resist to existing one
            if damType is not None and (
                damType not in resists or resists[damType] != resist
            ):
                resists[damType] = resist
                report(state.mobs[0])
        else:
            # first or otherwise new mob
            mobs = state.mobs
            damType = state.previousSpell.damType
            resists[damType] = resist
            mobs.insert(0, MobResist(mobname, resists))  # add to front
            report(state.mobs[0])
            state = state._replace(previousDead=False)

    tfeval("/edit -c0 resist_scream")
    tfeval("/edit -c0 resist_writhe")
    tfeval("/edit -c0 resist_shudder")
    tfeval("/edit -c0 resist_grunt")
    tfeval("/edit -c0 resist_wince")
    tfeval("/edit -c0 resist_shrug")


def scream(mobname: str):
    resists(Resist.SCREAM, mobname)


def writhe(mobname: str):
    resists(Resist.WRITHE, mobname)


def shudder(mobname: str):
    resists(Resist.SHUDDER, mobname)


def grunt(mobname: str):
    resists(Resist.GRUNT, mobname)


def wince(mobname: str):
    resists(Resist.WINCE, mobname)


def shrug(mobname: str):
    resists(Resist.SHRUG, mobname)


def reset(args: str):
    global state
    state = state._replace(previousDead=True)
    tfeval("/edit -c0 resist_scream")
    tfeval("/edit -c0 resist_writhe")
    tfeval("/edit -c0 resist_shudder")
    tfeval("/edit -c0 resist_grunt")
    tfeval("/edit -c0 resist_wince")
    tfeval("/edit -c0 resist_shrug")


def setup():
    cmds: Sequence[str] = [
        "/def -i -F -p10 -mglob -t`spec_spell: You watch with self-pride as your *` spell_hits = /python_call resists.hits \%-7",
        "/def -i -F -p10 -c0 -mglob -t`spec_spell: * screams in pain.` resist_scream = /python_call resists.scream \%-L3",
        "/def -i -F -p10 -c0 -mglob -t`spec_spell: * writhes in agony.` resist_writhe = /python_call resists.writhe \%-L3",
        "/def -i -F -p10 -c0 -mglob -t`spec_spell: * shudders from the force of the attack.` resist_shudder = /python_call resists.shudder \%-L7",
        "/def -i -F -p10 -c0 -mglob -t`spec_spell: * grunts from the pain.` resist_grunt = /python_call resists.grunt \%-L4",
        "/def -i -F -p10 -c0 -mglob -t`spec_spell: * winces a little from the pain.` resist_wince = /python_call resists.wince \%-L6",
        "/def -i -F -p10 -c0 -mglob -t`spec_spell: * shrugs off the attack.` resist_shrug = /python_call resists.shrug \%-L4",
        "/def -i -F -p10 -msimple -t`Astounding!  You can see things no one else can see, such as pk_trigger_starts.` resist_reset = /python_call resists.reset",
    ]

    for cmd in cmds:
        tfeval(cmd)

    tfprint("Loaded resists.py")


state = State(None, None, True, [])
setup()
