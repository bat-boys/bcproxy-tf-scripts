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

from spells import (
    DamType,
    DAMTYPE_STR,
    getSpellByName,
    getSpellByType,
    Spell,
    SpellType,
)
from utils import flatten, NoValue, tfprint


class Category(NoValue):
    BLAST_BIG = "blast_big"
    BLAST_SMALL = "blast_small"
    HEAL = "heal"
    PROT = "prot"
    UTILITY = "utility"


class CategoryBind(NamedTuple):
    key: str
    category: Category
    explanation: str


SPELL_BIND_ID = Literal["Q", "W", "E", "R", "T", "A", "S", "D", "F", "G"]


class SpellBind(NamedTuple):
    key: str
    spellBindId: SPELL_BIND_ID
    atTarget: bool


CategoryBinds = Sequence[Sequence[CategoryBind]]
SpellBinds = Sequence[SpellBind]
PartyReportSpellTypes = FrozenSet[SpellType]
PartyReportSpells = FrozenSet[Spell]
SpellsForCategory = Mapping[Category, Mapping[SPELL_BIND_ID, Optional[Spell]]]


class State(NamedTuple):
    category: Category
    target: Optional[str]
    categoryBinds: CategoryBinds
    spellsForCategory: SpellsForCategory
    spellBinds: SpellBinds
    partyReportSpells: PartyReportSpells
    partyReportSpellTypes: PartyReportSpellTypes


def categoryBindHelp(category: Category, categoryBinds: CategoryBinds) -> str:
    getCatStr: Callable[[CategoryBind], str] = (
        lambda cb: "@{Crgb550}" + cb.explanation + "@{n}"
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

    getSpellName: Callable[[Optional[Spell]], Optional[str]] = (
        lambda spell: cast(Spell, spell).name if spell != None else None
    )

    getSpellDamType: Callable[[Optional[Spell]], Optional[str]] = (
        lambda spell: DAMTYPE_STR[cast(Spell, spell).damType] if spell != None else None
    )

    getSpellStr: Callable[[SpellBind], Optional[str]] = (
        lambda sb: "{0}: {1:4} {2}".format(
            sb.spellBindId,
            getSpellDamType(spells[sb.spellBindId]),
            getSpellName(spells[sb.spellBindId]),
        )
        if sb.spellBindId in spells and spells[sb.spellBindId] != None
        else None
    )

    return "\n".join(
        [
            s
            for s in map(
                getSpellStr, filter(lambda spell: spell.atTarget == False, spellBinds)
            )
            if s is not None
        ]
    )


def changeCategory(category_raw: str):
    global state
    cat = category_raw.upper()
    category = Category[cat]
    state = state._replace(category=category)
    tfprint(categoryBindHelp(state.category, state.categoryBinds))
    tfprint(
        categorySpellsHelp(state.category, state.spellsForCategory, state.spellBinds)
    )


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

            tfeval("@cast {0}".format(castStr))
            tfprint("casting {0}".format(castStr))
            if partyReportCast(
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


state = State(Category.BLAST_BIG, None, [], {}, [], frozenset(), frozenset())


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
        "/def -i -F -msimple -t`You start chanting.` spell_start = "
        + "/echo -p @{Crgb450}»@{n} @{Cbgrgb110}@{BCrgb151} ---- CAST STARTED ---- @{n}",
        "/def -i -F -msimple -agGL -t`∴cast_cancelled` bcproxy_gag_cast_cancelled = "
        + "/echo -p @{Crgb450}»@{n} @{Cbgrgb110}@{BCrgb511} ---- CAST STOPPED ---- @{n}",
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
