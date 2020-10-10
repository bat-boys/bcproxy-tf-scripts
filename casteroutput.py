import dill  # type: ignore
from multiprocessing.connection import Listener
from os import getuid
from typing import cast, Callable, Optional

from castertypes import (
    Category,
    CategoryBind,
    CategoryBinds,
    SPELL_BIND_ID,
    PartyReportSpellTypes,
    PartyReportSpells,
    SpellBind,
    SpellBinds,
    SpellsForCategory,
    State,
)
from spells import (
    DamType,
    getDamtypeColor,
    Spell,
)
from utils import Color, colorize


SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-caster".format(getuid())

YELLOW = Color(0xFF, 0xFF, 0)


def draw(s):
    print("\033c", end="")  # clear screen
    print(s)


def categoryBindHelp(category: Category, categoryBinds: CategoryBinds) -> str:
    getCatStr: Callable[[CategoryBind], str] = (
        lambda cb: colorize(cb.explanation, YELLOW)
        if cb.category == category
        else cb.explanation
    )
    return "\n".join(map(lambda cbs: " ".join(map(getCatStr, cbs)), categoryBinds))


def categorySpellsHelp(
    category: Category, spellsForCategory: SpellsForCategory, spellBinds: SpellBinds
) -> str:
    if category not in spellsForCategory:
        return "no spells"

    spells = spellsForCategory[category]

    getSpellName: Callable[[Optional[Spell]], str] = (
        lambda spell: spell.name if spell is not None else ""
    )

    getSpellDamType: Callable[[Optional[Spell]], str] = (
        lambda spell: colorize(
            "{0:4}".format(spell.damType.value[:4]),
            getDamtypeColor(spell.damType),
        )
        if spell is not None and spell.damType is not None
        else "    "
    )

    getSpellStr: Callable[[SpellBind], Optional[str]] = (
        lambda sb: "{0}: {1:>4} {2}".format(
            sb.spellBindId,
            getSpellDamType(spells[sb.spellBindId]),
            getSpellName(spells[sb.spellBindId])[:25],
        )
        if sb.spellBindId in spells and spells[sb.spellBindId] is not None
        else None
    )

    return "\n".join(
        [
            s
            for s in map(
                getSpellStr,
                filter(lambda spellBind: spellBind.atTarget == False, spellBinds),
            )
            if s is not None
        ]
    )


with Listener(SOCKET_FILE, "AF_UNIX") as listener:
    print("listening to connections on {0}".format(SOCKET_FILE))

    while True:
        with listener.accept() as conn:
            print("connection opened", listener.last_accepted)

            while True:
                try:
                    state = cast(State, dill.loads(conn.recv_bytes()))
                    helptext = (
                        categoryBindHelp(state.category, state.categoryBinds)
                        + "\n"
                        + categorySpellsHelp(
                            state.category, state.spellsForCategory, state.spellBinds
                        )
                    )
                    draw(helptext)
                except EOFError:
                    print("connection closed")
                    break
