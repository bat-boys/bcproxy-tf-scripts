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
    Union,
)

from utils import flatten, NoValue, tfprint


class DamType(NoValue):
    ACID = "acid"
    ASPHYXIATION = "asphyxiation"
    COLD = "cold"
    ELECTRICITY = "electricity"
    FIRE = "fire"
    MAGICAL = "magical"
    POISON = "poison"
    PSI = "psi"
    HARM = "harm"
    PHYSICAL = "physical"


class SpellType(NoValue):
    MAGE_SINGLE_1 = "mage_single_1"  # biggest, requires reagent
    MAGE_SINGLE_2 = "mage_single_2"
    MAGE_SINGLE_3 = "mage_single_3"
    MAGE_SINGLE_4 = "mage_single_4"
    MAGE_SINGLE_5 = "mage_single_5"
    MAGE_AREA_1 = "mage_area_1"  # biggest
    MAGE_AREA_2 = "mage_area_2"
    MAGE_PROT_1 = "mage_prot_1"  # greater
    MAGE_PROT_2 = "mage_prot_2"
    CHANNELLER_SINGLE = "channeller_single"


class Spell(NamedTuple):
    name: str
    blast: bool


TYPE_SPELLS: Mapping[DamType, Mapping[SpellType, Spell]] = {
    DamType.ACID: {
        SpellType.MAGE_SINGLE_1: Spell("acid blast", True),
        SpellType.MAGE_SINGLE_2: Spell("acid ray", True),
        SpellType.MAGE_SINGLE_3: Spell("acid arrow", True),
        SpellType.MAGE_SINGLE_4: Spell("acid wind", True),
        SpellType.MAGE_SINGLE_5: Spell("disruption", True),
        SpellType.MAGE_AREA_1: Spell("acid storm", True),
        SpellType.MAGE_AREA_2: Spell("acid rain", True),
        SpellType.MAGE_PROT_1: Spell("acid shield", False),
        SpellType.MAGE_PROT_2: Spell("corrosion shield", False),
    },
    DamType.ASPHYXIATION: {
        SpellType.MAGE_SINGLE_1: Spell("blast vacuum", True),
        SpellType.MAGE_SINGLE_2: Spell("strangulation", True),
        SpellType.MAGE_SINGLE_3: Spell("chaos bolt", True),
        SpellType.MAGE_SINGLE_4: Spell("suffocation", True),
        SpellType.MAGE_SINGLE_5: Spell("vacuumbolt", True),
        SpellType.MAGE_AREA_1: Spell("vacuum globe", True),
        SpellType.MAGE_AREA_2: Spell("vacuum ball", True),
        SpellType.MAGE_PROT_1: Spell("aura of wind", False),
        SpellType.MAGE_PROT_2: Spell("ether boundary", False),
    },
    DamType.COLD: {
        SpellType.MAGE_SINGLE_1: Spell("cold ray", True),
        SpellType.MAGE_SINGLE_2: Spell("icebolt", True),
        SpellType.MAGE_SINGLE_3: Spell("darkfire", True),
        SpellType.MAGE_SINGLE_4: Spell("flaming ice", True),
        SpellType.MAGE_SINGLE_5: Spell("chill touch", True),
        SpellType.MAGE_AREA_1: Spell("hailstorm", True),
        SpellType.MAGE_AREA_2: Spell("cone of cold", True),
        SpellType.MAGE_PROT_1: Spell("frost shield", False),
        SpellType.MAGE_PROT_2: Spell("frost insulation", False),
    },
    DamType.ELECTRICITY: {
        SpellType.MAGE_SINGLE_1: Spell("electrocution", True),
        SpellType.MAGE_SINGLE_2: Spell("forked lightning", True),
        SpellType.MAGE_SINGLE_3: Spell("blast lightning", True),
        SpellType.MAGE_SINGLE_4: Spell("lightning bolt", True),
        SpellType.MAGE_SINGLE_5: Spell("shocking grasp", True),
        SpellType.MAGE_AREA_1: Spell("lightning storm", True),
        SpellType.MAGE_AREA_2: Spell("chain lightning", True),
        SpellType.MAGE_PROT_1: Spell("lightning shield", False),
        SpellType.MAGE_PROT_2: Spell("energy channeling", False),
        SpellType.CHANNELLER_SINGLE: Spell("channelbolt", True),
    },
    DamType.FIRE: {
        SpellType.MAGE_SINGLE_1: Spell("lava blast", True),
        SpellType.MAGE_SINGLE_2: Spell("meteor blast", True),
        SpellType.MAGE_SINGLE_3: Spell("fire blast", True),
        SpellType.MAGE_SINGLE_4: Spell("firebolt", True),
        SpellType.MAGE_SINGLE_5: Spell("flame arrow", True),
        SpellType.MAGE_AREA_1: Spell("lava storm", True),
        SpellType.MAGE_AREA_2: Spell("meteor swarm", True),
        SpellType.MAGE_PROT_1: Spell("flame shield", False),
        SpellType.MAGE_PROT_2: Spell("heat reduction", False),
        SpellType.CHANNELLER_SINGLE: Spell("channelburn", True),
    },
    DamType.MAGICAL: {
        SpellType.MAGE_SINGLE_1: Spell("golden arrow", True),
        SpellType.MAGE_SINGLE_2: Spell("summon greater spores", True),
        SpellType.MAGE_SINGLE_3: Spell("levin bolt", True),
        SpellType.MAGE_SINGLE_4: Spell("summon lesser spores", True),
        SpellType.MAGE_SINGLE_5: Spell("magic missile", True),
        SpellType.MAGE_AREA_1: Spell("magic eruption", True),
        SpellType.MAGE_AREA_2: Spell("magic wave", True),
        SpellType.MAGE_PROT_1: Spell("repulsor aura", False),
        SpellType.MAGE_PROT_2: Spell("magic dispersion", False),
        SpellType.CHANNELLER_SINGLE: Spell("channelball", True),
    },
    DamType.POISON: {
        SpellType.MAGE_SINGLE_1: Spell("summon carnal spores", True),
        SpellType.MAGE_SINGLE_2: Spell("power blast", True),
        SpellType.MAGE_SINGLE_3: Spell("venom strike", True),
        SpellType.MAGE_SINGLE_4: Spell("poison blast", True),
        SpellType.MAGE_SINGLE_5: Spell("thorn spray", True),
        SpellType.MAGE_AREA_1: Spell("killing cloud", True),
        SpellType.MAGE_AREA_2: Spell("poison spray", True),
        SpellType.MAGE_PROT_1: Spell("shield of detoxification", False),
        SpellType.MAGE_PROT_2: Spell("toxic dilution", False),
    },
    DamType.PHYSICAL: {
        SpellType.MAGE_PROT_1: Spell("armour of aether", False),
        SpellType.MAGE_PROT_2: Spell("force absorption", False),
    },
}


class OtherCategory(NoValue):
    CHANNELLER_DRAIN = "channeller_drain"


Category = Union[DamType, OtherCategory]


class CategoryBind(NamedTuple):
    key: str
    category: Category
    explanation: str


CATEGORY_BINDS: Sequence[Sequence[CategoryBind]] = [
    [
        CategoryBind("^[1", DamType.MAGICAL, "1: magical"),
        CategoryBind("^[2", DamType.FIRE, "2: fire"),
        CategoryBind("^[3", DamType.ELECTRICITY, "3: elec"),
        CategoryBind("^[4", DamType.ASPHYXIATION, "4: asphy"),
        CategoryBind("^[5", DamType.ACID, "5: acid"),
        CategoryBind("^[6", DamType.POISON, "6: poison"),
        CategoryBind("^[!", OtherCategory.CHANNELLER_DRAIN, "^1: drain"),
        CategoryBind("^[&", DamType.COLD, "^6: cold"),
    ],
]


class State(NamedTuple):
    category: Category
    blastTarget: Optional[str]
    protTarget: Optional[str]


def categoryBindHelp(category: Category) -> str:
    getCatStr: Callable[[CategoryBind], str] = (
        lambda cb: "@{Crgb550}" + cb.explanation + "@{n}"
        if cb.category == category
        else cb.explanation
    )
    return "\n".join(map(lambda cbs: " ".join(map(getCatStr, cbs)), CATEGORY_BINDS))


SPELL_NUMBER = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


class SpellBind(NamedTuple):
    key: str
    spellNumber: SPELL_NUMBER
    explanation: str


SPELL_BINDS: Sequence[SpellBind] = [
    SpellBind("^[q", "1", "Q"),
    SpellBind("^[w", "2", "W"),
    SpellBind("^[e", "3", "E"),
    SpellBind("^[r", "4", "R"),
    SpellBind("^[t", "5", "T"),
    SpellBind("^[a", "6", "A"),
    SpellBind("^[s", "7", "S"),
    SpellBind("^[d", "8", "D"),
    SpellBind("^[f", "9", "F"),
    SpellBind("^[g", "10", "G"),
]

SPELLS_FOR_CATEGORY: Mapping[Category, Mapping[SPELL_NUMBER, Spell]] = {
    DamType.MAGICAL: {
        "1": TYPE_SPELLS[DamType.MAGICAL][SpellType.CHANNELLER_SINGLE],
        "3": Spell("channelspray", True),
        "6": TYPE_SPELLS[DamType.MAGICAL][SpellType.MAGE_PROT_1],
    },
    DamType.FIRE: {
        "1": TYPE_SPELLS[DamType.FIRE][SpellType.CHANNELLER_SINGLE],
        "3": Spell("channelspray", True),
        "6": TYPE_SPELLS[DamType.FIRE][SpellType.MAGE_PROT_1],
    },
    DamType.ELECTRICITY: {
        "1": TYPE_SPELLS[DamType.ELECTRICITY][SpellType.CHANNELLER_SINGLE],
        "3": Spell("channelspray", True),
        "6": TYPE_SPELLS[DamType.ELECTRICITY][SpellType.MAGE_PROT_1],
    },
    DamType.ASPHYXIATION: {
        "1": TYPE_SPELLS[DamType.ASPHYXIATION][SpellType.MAGE_SINGLE_1],
        "2": TYPE_SPELLS[DamType.ASPHYXIATION][SpellType.MAGE_SINGLE_2],
        "3": TYPE_SPELLS[DamType.ASPHYXIATION][SpellType.MAGE_AREA_1],
        "6": TYPE_SPELLS[DamType.ASPHYXIATION][SpellType.MAGE_PROT_1],
    },
    DamType.ACID: {
        "1": TYPE_SPELLS[DamType.ACID][SpellType.MAGE_SINGLE_1],
        "2": TYPE_SPELLS[DamType.ACID][SpellType.MAGE_SINGLE_2],
        "3": TYPE_SPELLS[DamType.ACID][SpellType.MAGE_AREA_1],
        "6": TYPE_SPELLS[DamType.ACID][SpellType.MAGE_PROT_1],
    },
    DamType.POISON: {
        "1": TYPE_SPELLS[DamType.POISON][SpellType.MAGE_SINGLE_1],
        "2": TYPE_SPELLS[DamType.POISON][SpellType.MAGE_SINGLE_2],
        "3": TYPE_SPELLS[DamType.POISON][SpellType.MAGE_AREA_1],
        "6": TYPE_SPELLS[DamType.POISON][SpellType.MAGE_PROT_1],
    },
}


def categorySpellsHelp(category: Category) -> str:
    if category not in SPELLS_FOR_CATEGORY:
        return "no spells"

    spells = SPELLS_FOR_CATEGORY[category]

    getSpellStr: Callable[[SpellBind], Optional[str]] = (
        lambda sb: "{0}: {1}".format(sb.explanation, spells[sb.spellNumber].name)
        if sb.spellNumber in spells
        else None
    )

    return "\n".join([s for s in map(getSpellStr, SPELL_BINDS) if s is not None])


def changeCategory(category_raw: str):
    global state
    cat = category_raw.upper()
    selected = cast(
        Category, DamType[cat] if cat in DamType.__members__ else OtherCategory[cat]
    )
    state = state._replace(category=selected)
    tfprint(categoryBindHelp(selected))
    tfprint(categorySpellsHelp(selected))


def castSpell(spellNumber: SPELL_NUMBER):
    global state
    if (
        state.category in SPELLS_FOR_CATEGORY
        and spellNumber in SPELLS_FOR_CATEGORY[state.category]
    ):
        spell = SPELLS_FOR_CATEGORY[state.category][spellNumber]
        eval("@cast {0}".format(spell.name))
        tfprint("casting {0}".format(spell.name))


def setup():
    for key, category, explanation in flatten(CATEGORY_BINDS):
        eval(
            "/def -i -q -b'{0}' = /python_call blaster.changeCategory {1}".format(
                key, category.value
            )
        )
    for key, category, explanation in SPELL_BINDS:
        eval(
            "/def -i -q -b'{0}' = /python_call blaster.castSpell {1}".format(
                key, category
            )
        )
    tfprint("Loaded blaster.py")


setup()
state = State(DamType.MAGICAL, None, None)
