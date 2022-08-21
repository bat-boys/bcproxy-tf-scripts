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
        "E": getSpellByType(DamType.COLD, SpellType.MAGE_SINGLE_1),
        "A": getSpellByType(DamType.MAGICAL, SpellType.MAGE_SINGLE_1),
        "S": getSpellByType(DamType.FIRE, SpellType.MAGE_SINGLE_1),
        # area
        "R": getSpellByType(DamType.ASPHYXIATION, SpellType.MAGE_AREA_1),
        "D": getSpellByType(DamType.ACID, SpellType.MAGE_AREA_1),
        "F": getSpellByName("prismatic burst"),
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
        "E": getSpellByName("floating"),
        "A": getSpellByName("displacement"),
        "S": getSpellByName("blurred image"),
        "D": getSpellByName("shield of protection"),
        "F": getSpellByName("iron will"),
    },
    Category.UTILITY: {
        "A": getSpellByName("shelter"),
        "S": getSpellByName("neutralize field"),
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
            getSpellByName("shelter"),
            getSpellByName("neutralize field"),
        ]
    )
)


def setup():
    cmds: Sequence[str] = [
        "/def t = /python_call party.changeTargetName \%*",
        "/def f = /python_call ginfo.finger \%*",
        "/def c = /python_call mobinfo.moblook \%*",
        "/def pginfo = /python_call party.ginfo",
        "/def cr = /python_call shipnav.cruise \%*",
        "/def -i -q -b'^[z' = @cast stop",
        "/def -i -q -b'^[x' = @party prots",
        "/def -i -q -b'^[c' = @show effects",
        "/def -i -q -b'^[ ' = /python_call party.manualPs",
        "/def -i -q -b'^[v' = /python_call resists.reportLast",
        "/def key_f2 = @eqs int",
        "/def key_f3 = @eqs wis",
        "/def key_f4 = @eqs spr",
        "/def key_f5 = @eqs blast",
        "/def -i -F -msimple -ag -t`You feel your staff touching your mind.` gag_staff_ceremony",
        "/def -i -F -msimple -ag -t`You surreptitiously conceal your spell casting.` gag_conceal",
        "/def -i -F -p10 -msimple -ag -t`spec_spell: Power flows from your staff to the spell.` gag_staff_cheapen",
        "/def -i -F -p10 -msimple -ag -t`spec_spell: Your fine choice of components lowers the effort of the spell.` gag_power_regs",
        "/def -i -F -p10 -mglob -ag -t`spec_spell: You pull out * which bursts into a zillion technicolour sparkles!` gag_acid",
        "/def -i -F -p10 -msimple -ag -t`spec_spell: Your knowledge in elemental powers helps you to save the reagent for further use.` gag_reagent_save",
        "/def -i -F -p10 -mglob -t`You are standing in a flat stone terrace. *` inner_mellon = @say mellon;study",
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
