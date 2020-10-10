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
    Spell,
    SpellType,
)
from utils import NoValue


class Category(NoValue):
    BLAST_BIG = "blast_big"
    BLAST_SMALL = "blast_small"
    HEAL = "heal"
    TYPEPROT = "typeprot"
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
    currentSpell: Optional[str]
