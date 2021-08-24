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
        CategoryBind("^[1", Category.HEAL, "1: heal"),
        CategoryBind("^[2", Category.PROT, "2: prot"),
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
    Category.HEAL: {
        "Q": getSpellByName("cure light wounds"),
        "W": getSpellByName("cure serious wounds"),
        "E": getSpellByName("cure critical wounds"),
        "R": getSpellByName("major heal"),
        "A": getSpellByName("minor party heal"),
        "S": getSpellByName("major party heal"),
        "D": getSpellByName("deaths door"),
    },
    Category.PROT: {
        "Q": getSpellByName("unstun"),
        "W": getSpellByName("unpain"),
    },
}

PARTY_REPORT_SPELL_TYPES: PartyReportSpellTypes = frozenset([])
PARTY_REPORT_SPELLS: PartyReportSpells = frozenset(
    filterOutNones(
        [
            getSpellByName("deaths door"),
        ]
    )
)


def setup():
    cmds: Sequence[str] = [
        "/def t = /python_call party.changeTargetName \%*",
        "/def f = /python_call ginfo.finger \%*",
        "/def pginfo = /python_call party.ginfo",
        "/def -i -q -b'^[z' = @cast stop",
        "/def -i -q -b'^[x' = @party prots",
        "/def -i -q -b'^[c' = @show effects",
        "/def -i -q -b'^[ ' = /python_call party.manualPs",
        "/def key_f2 = @ch heal",
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
