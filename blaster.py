from enum import Enum
from termcolor import colored
from tf import eval as tfeval  # type: ignore
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


from caster import (
    Category,
    CategoryBind,
    CategoryBinds,
    PartyReportSpells,
    PartyReportSpellTypes,
    setup as setupCaster,
    SpellBind,
    SpellBinds,
    SpellsForCategory,
)
from spells import DamType, getSpellByName, getSpellByType, Spell, SpellType
from utils import filterOutNones, flatten, NoValue, tfprint

CATEGORY_BINDS: CategoryBinds = [
    [
        CategoryBind("^[1", Category.BLAST_BIG, "1: blast"),
        CategoryBind("^[2", Category.PROT, "2: prot"),
        CategoryBind("^[3", Category.UTILITY, "3: utility"),
        CategoryBind("^[4", Category.BLAST_SMALL, "4: blast small"),
    ],
]

SPELL_BINDS: SpellBinds = [
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

SPELLS_FOR_CATEGORY: SpellsForCategory = {
    Category.BLAST_BIG: {
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
    Category.PROT: {
        "Q": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_PROT_1),
        "W": getSpellByType(DamType.ACID, SpellType.MAGE_PROT_1),
        "E": getSpellByType(DamType.POISON, SpellType.MAGE_PROT_1),
        "R": getSpellByType(DamType.COLD, SpellType.MAGE_PROT_1),
        "A": getSpellByType(DamType.MAGICAL, SpellType.MAGE_PROT_1),
        "S": getSpellByType(DamType.FIRE, SpellType.MAGE_PROT_1),
        "D": getSpellByType(DamType.ELECTRICITY, SpellType.MAGE_PROT_1),
        "F": getSpellByType(DamType.PHYSICAL, SpellType.MAGE_PROT_1),
    },
    Category.BLAST_SMALL: {
        "Q": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_5),
        "W": getSpellByType(DamType.ACID, SpellType.MAGE_SINGLE_5),
        "E": getSpellByType(DamType.POISON, SpellType.MAGE_SINGLE_5),
        "A": getSpellByType(DamType.MAGICAL, SpellType.MAGE_SINGLE_5),
        "S": getSpellByType(DamType.FIRE, SpellType.MAGE_SINGLE_5),
        "D": getSpellByType(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_5),
        "R": getSpellByType(DamType.COLD, SpellType.MAGE_SINGLE_5),
    },
    Category.UTILITY: {
        "Q": getSpellByName("dispel magical protection"),
        "W": getSpellByName("resist dispel"),
        "A": getSpellByName("displacement"),
        "S": getSpellByName("blurred image"),
        "D": getSpellByName("shield of protection"),
    },
}

PARTY_REPORT_SPELL_TYPES: PartyReportSpellTypes = frozenset([SpellType.MAGE_PROT_1])
PARTY_REPORT_SPELLS: PartyReportSpells = frozenset(
    filterOutNones(
        [
            getSpellByName("dispel magical protection"),
            getSpellByName("resist dispel"),
        ]
    )
)


def setup():
    cmds: Sequence[str] = [
        "/def -i -q -b'^[z' = @cast stop",
        "/def -i -q -b'^[x' = @party prots",
        "/def -i -q -b'^[c' = @show effects",
        "/def -i -q -b'^[ ' = @ps;check supply",
        "/def key_f2 = @ch int",
        "/def key_f3 = @ch wis",
        "/def key_f4 = @ch spr",
    ]
    for cmd in cmds:
        tfeval(cmd)

    tfeval("/python_load caster")
    setupCaster(
        CATEGORY_BINDS,
        SPELLS_FOR_CATEGORY,
        SPELL_BINDS,
        PARTY_REPORT_SPELLS,
        PARTY_REPORT_SPELL_TYPES,
    )

    tfprint("Loaded blaster.py")


setup()
