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


from caster import setup as setupCaster
from castertypes import (
    Category,
    CategoryBind,
    CategoryBinds,
    PartyReportSpells,
    PartyReportSpellTypes,
    SpellBind,
    SpellBinds,
    SpellsForCategory,
)
from spells import DamType, getSpellByName, getSpellByType, Spell, SpellType
from tfutils import tfprint
from utils import filterOutNones, flatten

CATEGORY_BINDS: CategoryBinds = [
    [
        CategoryBind("^[1", Category.BLAST_BIG, "1: blast"),
        CategoryBind("^[2", Category.TYPEPROT, "2: typeprot"),
        CategoryBind("^[3", Category.PROT, "3: prot"),
    ],
    [
        CategoryBind("^[4", Category.UTILITY, "4: utility"),
        CategoryBind("^[5", Category.BLAST_SMALL, "5: small"),
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
    Category.TYPEPROT: {
        "Q": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_PROT_1),
        "W": getSpellByType(DamType.ACID, SpellType.MAGE_PROT_1),
        "E": getSpellByType(DamType.POISON, SpellType.MAGE_PROT_1),
        "R": getSpellByType(DamType.COLD, SpellType.MAGE_PROT_1),
        "A": getSpellByType(DamType.MAGICAL, SpellType.MAGE_PROT_1),
        "S": getSpellByType(DamType.FIRE, SpellType.MAGE_PROT_1),
        "D": getSpellByType(DamType.ELECTRICITY, SpellType.MAGE_PROT_1),
        "F": getSpellByType(DamType.PHYSICAL, SpellType.MAGE_PROT_1),
    },
    Category.PROT: {
        "Q": getSpellByName("dispel magical protection"),
        "W": getSpellByName("resist dispel"),
        "A": getSpellByName("displacement"),
        "S": getSpellByName("blurred image"),
        "D": getSpellByName("shield of protection"),
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

# You pull out a handful of olivine powder which bursts into a zillion technicolour sparkles!
# You watch with self-pride as your acid blast hits Poltergeist.
# Poltergeist screams in pain.


def setup():
    cmds: Sequence[str] = [
        "/def t = /python_call party.changeTargetName \%1",
        "/def -i -q -b'^[z' = @cast stop",
        "/def -i -q -b'^[x' = @party prots",
        "/def -i -q -b'^[c' = @show effects",
        "/def -i -q -b'^[ ' = @ps;check supply",
        "/def -i -q -b'^[v' = /python_call resists.reportLast",
        "/def key_f2 = @ch int",
        "/def key_f3 = @ch wis",
        "/def key_f4 = @ch spr",
        "/def -i -F -msimple -ag -t`Power flows from your staff to the spell.` gag_staff_cheapen",
        "/def -i -F -msimple -ag -t`Your fine choice of components lowers the effort of the spell.` gag_power_regs",
        "/def -i -F -msimple -ag -t`You surreptitiously conceal your spell casting.` gag_conceal",
        "/def -i -F -mglob -ag -t`You pull out * which bursts into a zillion technicolour sparkles!` gag_acid",
        "/def -i -F -msimple -ag -t`You feel your staff touching your mind.` gag_staff_ceremony",
        "/def -i -F -msimple -ag -t`Your knowledge in elemental powers helps you to save the reagent for further use.` gag_reagent_save",
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
