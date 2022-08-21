import dill  # type: ignore
from multiprocessing.connection import Client
from os import getuid
from tf import eval as tfeval  # type: ignore
from typing import (
    Callable,
    cast,
    FrozenSet,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Union,
)

from castertypes import (
    Category,
    CategoryBind,
    CategoryBinds,
    SPELL_BIND_ID,
    PartyReportSpellTypes,
    PartyReportSpells,
    SpellBinds,
    SpellsForCategory,
    State,
)
from spells import (
    DamType,
    getSpellByName,
    getSpellByType,
    Spell,
    SpellType,
)
from tfutils import tfprint
from utils import flatten, NoValue


SOCKET_FILE = "/var/run/user/{0}/bcproxy-tf-scripts-caster".format(getuid())
CONN = Client(SOCKET_FILE, "AF_UNIX")


def changeCategory(category_raw: str):
    global state
    cat = category_raw.upper()
    category = Category[cat]
    state = state._replace(category=category)
    CONN.send_bytes(dill.dumps(state))


def castString(spell: Spell, atTarget: bool, target: Optional[str]):
    # spell can't have target, cast always without
    if spell.withTarget == False:
        return spell.name

    # spell must have target, cast with it
    if spell.withoutTarget == False:
        return "{0} at {1}".format(spell.name, target)

    # spell can be cast with or without target, do according to pressed key
    if atTarget == True:
        return "{0} at {1}".format(spell.name, target)
    else:
        return spell.name


def castSpellWithTarget(spellBindId: SPELL_BIND_ID):
    castSpell(spellBindId, True)


def castSpellWithoutTarget(spellBindId: SPELL_BIND_ID):
    castSpell(spellBindId, False)


def castSpell(spellBindId: SPELL_BIND_ID, atTarget: bool):
    global state
    if (
        state.category in state.spellsForCategory
        and spellBindId in state.spellsForCategory[state.category]
    ):
        spell = state.spellsForCategory[state.category][spellBindId]

        if spell != None:
            spell = cast(Spell, spell)
            castStr = castString(spell, atTarget, state.target)
            state = state._replace(currentSpell=castStr)

            tfeval("@cast {0}".format(castStr))

            if atTarget or partyReportCast(
                spell, state.partyReportSpellTypes, state.partyReportSpells
            ):
                tfeval("@quote 'cast info' party report")


def setTarget(target: str):
    global state
    state = state._replace(target=target[:-1].lower())
    tfprint("target {0}".format(state.target))


def partyReportCast(
    spell: Spell, spellTypes: PartyReportSpellTypes, spells: PartyReportSpells
) -> bool:
    return spell.spellType in spellTypes or spell in spells


def castStart(args):
    global state
    cur: str = state.currentSpell if state.currentSpell != None else ""
    tfprint("@{Cbgrgb110}@{BCrgb151} ---- CAST STARTED " + cur + " ---- @{n}")


def castStop(args):
    global state
    state = state._replace(currentSpell=None)
    tfprint("@{Cbgrgb110}@{BCrgb511} ---- CAST STOPPED ---- @{n}")


state = State(Category.BLAST_BIG, None, [], {}, [], frozenset(), frozenset(), None)


def setup(
    categoryBinds: CategoryBinds,
    spellsForCategory: SpellsForCategory,
    spellBinds: SpellBinds,
    partyReportSpells: PartyReportSpells,
    partyReportSpellTypes: PartyReportSpellTypes,
):
    global state
    state = state._replace(
        categoryBinds=categoryBinds,
        spellsForCategory=spellsForCategory,
        spellBinds=spellBinds,
        partyReportSpells=partyReportSpells,
        partyReportSpellTypes=partyReportSpellTypes,
    )
    cmds: Sequence[str] = [
        "/def -i -F -msimple -ag -t`You start chanting.` spell_start = "
        + "/python_call caster.castStart",
        "/def -i -F -msimple -agGL -t`∴cast_cancelled` cast_cancelled = "
        + "/python_call caster.castStop",
        "/def -i -F -msimple -ag -t`You are done with the chant.` gag_spell_done",
        "/def -i -F -msimple -ag -t`You skillfully cast the spell with haste.` gag_haste",
        "/def -i -F -msimple -ag -t`You skillfully cast the spell with greater haste.` gag_ghaste",
        "/def -i -F -mglob -t`You are now targetting *` set_target = "
        + "/python_call caster.setTarget \%-4",
        "/def -i -F -mglob -t`You are now target-healing *` set_target_heal = "
        + "/python_call caster.setTarget \%-4",
    ]
    for cmd in cmds:
        tfeval(cmd)

    for key, category, explanation in flatten(state.categoryBinds):
        tfeval(
            "/def -i -q -b`{0}` = /python_call caster.changeCategory {1}".format(
                key, category.value
            )
        )

    for key, spellBindId, atTarget in spellBinds:
        if atTarget:
            tfeval(
                "/def -i -q -b`{0}` = /python_call caster.castSpellWithTarget {1}".format(
                    key, spellBindId
                )
            )
        else:
            tfeval(
                "/def -i -q -b`{0}` = /python_call caster.castSpellWithoutTarget {1}".format(
                    key, spellBindId
                )
            )

    tfprint("Loaded caster.py")
