from enum import Enum
from termcolor import colored
from tf import eval  # type: ignore
from typing import (
    Callable,
    cast,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    FrozenSet,
    Union,
)


from utils import flatten, NoValue, tfprint
from spells import DamType, getSpellByName, getSpellByType, Spell, SpellType


class OtherCategory(NoValue):
    BLAST_BIG = "blast_big"
    BLAST_SMALL = "blast_small"
    PROT = "prot"
    UTILITY = "utility"


Category = Union[DamType, OtherCategory]


class CategoryBind(NamedTuple):
    key: str
    category: Category
    explanation: str


CATEGORY_BINDS: Sequence[Sequence[CategoryBind]] = [
    [
        CategoryBind("^[1", OtherCategory.BLAST_BIG, "1: blast"),
        CategoryBind("^[2", OtherCategory.PROT, "2: prot"),
        CategoryBind("^[3", OtherCategory.UTILITY, "3: utility"),
        CategoryBind("^[4", OtherCategory.BLAST_SMALL, "4: blast small"),
    ],
]


class State(NamedTuple):
    category: Category
    target: Optional[str]


def categoryBindHelp(category: Category) -> str:
    getCatStr: Callable[[CategoryBind], str] = (
        lambda cb: "@{Crgb550}" + cb.explanation + "@{n}"
        if cb.category == category
        else cb.explanation
    )
    return "\n".join(map(lambda cbs: " ".join(map(getCatStr, cbs)), CATEGORY_BINDS))


SPELL_BIND_ID = Literal["Q", "W", "E", "R", "T", "A", "S", "D", "F", "G"]


class SpellBind(NamedTuple):
    key: str
    spellBindId: SPELL_BIND_ID
    atTarget: bool


SPELL_BINDS: Sequence[SpellBind] = [
    SpellBind("^[q", "Q", False),
    SpellBind("^[w", "W", False),
    SpellBind("^[e", "E", False),
    SpellBind("^[r", "R", False),
    SpellBind("^[t", "T", False),
    SpellBind("^[a", "A", False),
    SpellBind("^[s", "S", False),
    SpellBind("^[d", "D", False),
    SpellBind("^[f", "F", False),
    SpellBind("^[g", "G", False),
    SpellBind("^[Q", "Q", True),
    SpellBind("^[W", "W", True),
    SpellBind("^[E", "E", True),
    SpellBind("^[R", "R", True),
    SpellBind("^[T", "T", True),
    SpellBind("^[A", "A", True),
    SpellBind("^[S", "S", True),
    SpellBind("^[D", "D", True),
    SpellBind("^[F", "F", True),
    SpellBind("^[G", "G", True),
]

SPELLS_FOR_CATEGORY: Mapping[Category, Mapping[SPELL_BIND_ID, Optional[Spell]]] = {
    OtherCategory.BLAST_BIG: {
        "Q": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_1),
        "W": getSpellByType(DamType.ACID, SpellType.MAGE_SINGLE_1),
        "E": getSpellByType(DamType.POISON, SpellType.MAGE_SINGLE_1),
        # channeller
        "A": getSpellByType(DamType.MAGICAL, SpellType.CHANNELLER_SINGLE),
        "S": getSpellByType(DamType.FIRE, SpellType.CHANNELLER_SINGLE),
        "D": getSpellByType(DamType.ELECTRICITY, SpellType.CHANNELLER_SINGLE),
        "F": getSpellByName("drain enemy"),
        # area
        "R": getSpellByType(DamType.ACID, SpellType.MAGE_AREA_1),
        "T": getSpellByName("channelspray"),
    },
    OtherCategory.PROT: {
        "Q": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_PROT_1),
        "W": getSpellByType(DamType.ACID, SpellType.MAGE_PROT_1),
        "E": getSpellByType(DamType.POISON, SpellType.MAGE_PROT_1),
        "R": getSpellByType(DamType.COLD, SpellType.MAGE_PROT_1),
        "A": getSpellByType(DamType.MAGICAL, SpellType.MAGE_PROT_1),
        "S": getSpellByType(DamType.FIRE, SpellType.MAGE_PROT_1),
        "D": getSpellByType(DamType.ELECTRICITY, SpellType.MAGE_PROT_1),
        "F": getSpellByType(DamType.PHYSICAL, SpellType.MAGE_PROT_1),
    },
    OtherCategory.BLAST_SMALL: {
        "Q": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_5),
        "W": getSpellByType(DamType.ACID, SpellType.MAGE_SINGLE_5),
        "E": getSpellByType(DamType.POISON, SpellType.MAGE_SINGLE_5),
        "A": getSpellByType(DamType.MAGICAL, SpellType.MAGE_SINGLE_5),
        "S": getSpellByType(DamType.FIRE, SpellType.MAGE_SINGLE_5),
        "D": getSpellByType(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_5),
        "R": getSpellByType(DamType.COLD, SpellType.MAGE_SINGLE_5),
    },
    OtherCategory.UTILITY: {
        "A": getSpellByName("displacement"),
        "S": getSpellByName("blurred image"),
        "D": getSpellByName("shield of protection"),
    },
}

DAMTYPE_STR: Mapping[Optional[DamType], str] = {
    DamType.ACID: "@{Cgreen}" + "{:4}".format(DamType.ACID.value[:4]) + "@{n}",
    DamType.ASPHYXIATION: "@{BCmagenta}"
    + "{:4}".format(DamType.ASPHYXIATION.value[:4])
    + "@{n}",
    DamType.COLD: "@{BCcyan}" + "{:4}".format(DamType.COLD.value[:4]) + "@{n}",
    DamType.ELECTRICITY: "@{BCblue}"
    + "{:4}".format(DamType.ELECTRICITY.value[:4])
    + "@{n}",
    DamType.FIRE: "@{Cred}" + "{:4}".format(DamType.FIRE.value[:4]) + "@{n}",
    DamType.MAGICAL: "@{BCyellow}" + "{:4}".format(DamType.MAGICAL.value[:4]) + "@{n}",
    DamType.POISON: "@{Cgreen}" + "{:4}".format(DamType.POISON.value[:4]) + "@{n}",
    DamType.PSI: "@{BCblue}" + "{:4}".format(DamType.PSI.value[:4]) + "@{n}",
    DamType.HARM: "@{BCyellow}" + "{:4}".format(DamType.HARM.value[:4]) + "@{n}",
    DamType.PHYSICAL: "@{Cyellow}" + "{:4}".format(DamType.PHYSICAL.value[:4]) + "@{n}",
    None: "    ",
}


def categorySpellsHelp(category: Category) -> str:
    if category not in SPELLS_FOR_CATEGORY:
        return "no spells"

    spells = SPELLS_FOR_CATEGORY[category]

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
                getSpellStr, filter(lambda spell: spell.atTarget == False, SPELL_BINDS)
            )
            if s is not None
        ]
    )


class Resist(NamedTuple):
    regex: str
    percentage: int


RESISTS: FrozenSet[Resist] = frozenset(
    [
        Resist("screams in pain\.", 0),
        Resist("writhes in agony\.", 20),
        Resist("shudders from the force of the attack\.", 40),
        Resist("grunts from the pain\.", 60),
        Resist("winces a little from the pain\.", 80),
        Resist("shrugs off the attack\.", 100),
    ]
)


def partyReportCast(spell: Spell):
    if spell.spellType == SpellType.MAGE_PROT_1:
        return True
    return False


def changeCategory(category_raw: str):
    global state
    cat = category_raw.upper()
    selected = cast(
        Category, DamType[cat] if cat in DamType.__members__ else OtherCategory[cat]
    )
    state = state._replace(category=selected)
    tfprint(categoryBindHelp(selected))
    tfprint(categorySpellsHelp(selected))


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
        state.category in SPELLS_FOR_CATEGORY
        and spellBindId in SPELLS_FOR_CATEGORY[state.category]
    ):
        spell = SPELLS_FOR_CATEGORY[state.category][spellBindId]

        if spell != None:
            spell = cast(Spell, spell)
            castStr = castString(spell, atTarget, state.target)

            eval("@cast {0}".format(castStr))
            tfprint("casting {0}".format(castStr))
            if partyReportCast(spell):
                eval("@quote 'cast info' party report")


def setTarget(target: str):
    global state
    state = state._replace(target=target[:-1].lower())
    tfprint("target {0}".format(state.target))


SETUP_COMMANDS: Sequence[str] = [
    "/def -i -q -b'^[z' = @cast stop",
    "/def -i -q -b'^[-' = @party prots",
    "/def -i -q -b'^[ ' = @ps",
    "/def -i -q -b'^[ ' = @ps",
    "/def key_f2 = @ch int",
    "/def key_f2 = @ch wis",
    "/def key_f2 = @ch spr",
    '/def -i -F -msimple -t"You start chanting." spell_start = '
    + "/echo -p @{Crgb450}»@{n} @{Cbgrgb110}@{BCrgb151} ---- CAST STARTED ---- @{n}",
    '/def -i -F -msimple -agGL -t"∴cast_cancelled" bcproxy_gag_cast_cancelled = '
    + "/echo -p @{Crgb450}»@{n} @{Cbgrgb110}@{BCrgb511} ---- CAST STOPPED ---- @{n}",
    '/def -i -F -msimple -ag -t"You skillfully cast the spell with haste." gag_haste',
    '/def -i -F -msimple -ag -t"You skillfully cast the spell with greater haste." gag_ghaste',
    '/def -i -F -mglob -t"You are now targetting *" set_target = /python_call blaster.setTarget \%-4',
    '/def -i -F -mglob -t"You are now target-healing *" set_target_heal = /python_call blaster.setTarget \%-4',
]


def setup():
    for key, category, explanation in flatten(CATEGORY_BINDS):
        eval(
            "/def -i -q -b'{0}' = /python_call blaster.changeCategory {1}".format(
                key, category.value
            )
        )

    for key, spellBindId, atTarget in SPELL_BINDS:
        if atTarget:
            eval(
                "/def -i -q -b'{0}' = /python_call blaster.castSpellWithTarget {1}".format(
                    key, spellBindId
                )
            )
        else:
            eval(
                "/def -i -q -b'{0}' = /python_call blaster.castSpellWithoutTarget {1}".format(
                    key, spellBindId
                )
            )

    for cmd in SETUP_COMMANDS:
        eval(cmd)

    tfprint("Loaded blaster.py")


setup()
state = State(DamType.MAGICAL, None)
