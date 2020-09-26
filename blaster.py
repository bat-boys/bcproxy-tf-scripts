from tf import out, eval # type: ignore
from typing import Callable, cast, NamedTuple, Optional, Union
from enum import Enum

def tfprint(s: str):
    lines = map(lambda l: "» {0}".format(l), s.split('\n'))
    out('\n'.join(lines))

class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

class DamType(NoValue):
    ACID = 'acid'
    ASPHYXIATION = 'asphyxiation'
    COLD = 'cold'
    ELECTRICITY = 'electricity'
    FIRE = 'fire'
    MAGICAL = 'magical'
    POISON = 'poison'
    PSI = 'psi'
    HARM = 'harm'
    PHYSICAL = 'physical'

class SpellType(NoValue):
    MAGE_SINGLE_1 ='mage_single_1' # biggest, requires reagent
    MAGE_SINGLE_2 ='mage_single_2'
    MAGE_SINGLE_3 ='mage_single_3'
    MAGE_SINGLE_4 ='mage_single_4'
    MAGE_SINGLE_5 ='mage_single_5'
    MAGE_AREA_1 = 'mage_area_1' # biggest
    MAGE_AREA_2 = 'mage_area_2'
    MAGE_PROT_1 = 'mage_prot_1' # greater
    MAGE_PROT_2 = 'mage_prot_2'
    CHANNELLER_SINGLE = 'channeller_single'

class TypeSpell(NamedTuple):
    damType: DamType
    spellType: SpellType
    spell: str

BLAST_SPELLS = (
    TypeSpell(DamType.ACID, SpellType.MAGE_SINGLE_1, 'acid blast'),
    TypeSpell(DamType.ACID, SpellType.MAGE_SINGLE_2, 'acid ray'),
    TypeSpell(DamType.ACID, SpellType.MAGE_SINGLE_3, 'acid arrow'),
    TypeSpell(DamType.ACID, SpellType.MAGE_SINGLE_4, 'acid wind'),
    TypeSpell(DamType.ACID, SpellType.MAGE_SINGLE_5, 'disruption'),
    TypeSpell(DamType.ACID, SpellType.MAGE_AREA_1, 'acid storm'),
    TypeSpell(DamType.ACID, SpellType.MAGE_AREA_2, 'acid rain'),
    TypeSpell(DamType.ACID, SpellType.MAGE_PROT_1, 'acid shield'),
    TypeSpell(DamType.ACID, SpellType.MAGE_PROT_2, 'corrosion shield'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_1, 'blast vacuum'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_2, 'strangulation'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_3, 'chaos bolt'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_4, 'suffocation'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_5, 'vacuumbolt'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_AREA_1, 'vacuum globe'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_AREA_2, 'vacuum ball'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_PROT_1, 'aura of wind'),
    TypeSpell(DamType.ASPHYXIATION, SpellType.MAGE_PROT_2, 'ether boundary'),
    TypeSpell(DamType.COLD, SpellType.MAGE_SINGLE_1, 'cold ray'),
    TypeSpell(DamType.COLD, SpellType.MAGE_SINGLE_2, 'icebolt'),
    TypeSpell(DamType.COLD, SpellType.MAGE_SINGLE_3, 'darkfire'),
    TypeSpell(DamType.COLD, SpellType.MAGE_SINGLE_4, 'flaming ice'),
    TypeSpell(DamType.COLD, SpellType.MAGE_SINGLE_5, 'chill touch'),
    TypeSpell(DamType.COLD, SpellType.MAGE_AREA_1, 'hailstorm'),
    TypeSpell(DamType.COLD, SpellType.MAGE_AREA_2, 'cone of cold'),
    TypeSpell(DamType.COLD, SpellType.MAGE_PROT_1, 'frost shield'),
    TypeSpell(DamType.COLD, SpellType.MAGE_PROT_2, 'frost insulation'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_1, 'electrocution'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_2, 'forked lightning'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_3, 'blast lightning'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_4, 'lightning bolt'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_SINGLE_5, 'shocking grasp'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_AREA_1, 'lightning storm'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_AREA_2, 'chain lightning'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_PROT_1, 'lightning shield'),
    TypeSpell(DamType.ELECTRICITY, SpellType.MAGE_PROT_2, 'energy channeling'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_SINGLE_1, 'lava blast'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_SINGLE_2, 'meteor blast'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_SINGLE_3, 'fire blast'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_SINGLE_4, 'firebolt'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_SINGLE_5, 'flame arrow'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_AREA_1, 'lava storm'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_AREA_2, 'meteor swarm'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_PROT_1, 'flame shield'),
    TypeSpell(DamType.FIRE, SpellType.MAGE_PROT_2, 'heat reduction'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_SINGLE_1, 'golden arrow'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_SINGLE_2, 'summon greater spores'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_SINGLE_3, 'levin bolt'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_SINGLE_4, 'summon lesser spores'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_SINGLE_5, 'magic missile'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_AREA_1, 'magic eruption'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_AREA_2, 'magic wave'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_PROT_1, 'repulsor aura'),
    TypeSpell(DamType.MAGICAL, SpellType.MAGE_PROT_2, 'magic dispersion'),
    TypeSpell(DamType.POISON, SpellType.MAGE_SINGLE_1, 'summon carnal spores'),
    TypeSpell(DamType.POISON, SpellType.MAGE_SINGLE_2, 'power blast'),
    TypeSpell(DamType.POISON, SpellType.MAGE_SINGLE_3, 'venom strike'),
    TypeSpell(DamType.POISON, SpellType.MAGE_SINGLE_4, 'poison blast'),
    TypeSpell(DamType.POISON, SpellType.MAGE_SINGLE_5, 'thorn spray'),
    TypeSpell(DamType.POISON, SpellType.MAGE_AREA_1, 'killing cloud'),
    TypeSpell(DamType.POISON, SpellType.MAGE_AREA_2, 'poison spray'),
    TypeSpell(DamType.POISON, SpellType.MAGE_PROT_1, 'shield of detoxification'),
    TypeSpell(DamType.POISON, SpellType.MAGE_PROT_2, 'toxic dilution'),
    TypeSpell(DamType.ELECTRICITY, SpellType.CHANNELLER_SINGLE, 'channelbolt'),
    TypeSpell(DamType.FIRE, SpellType.CHANNELLER_SINGLE, 'channelburn'),
    TypeSpell(DamType.MAGICAL, SpellType.CHANNELLER_SINGLE, 'channelball'),
    TypeSpell(DamType.PHYSICAL, SpellType.MAGE_PROT_1, 'armour of aether'),
    TypeSpell(DamType.PHYSICAL, SpellType.MAGE_PROT_2, 'force absorption'),
)

class OtherCategory(NoValue):
    CHANNELLER_DRAIN = 'channeller_drain'

Category = Union[DamType, OtherCategory]

class CategoryBind(NamedTuple):
    key: str
    category: Category
    explanation: str

CATEGORY_BINDS = [
    [
        CategoryBind('^[1', DamType.MAGICAL, '1: magical'),
        CategoryBind('^[2', DamType.FIRE, '2: fire'),
        CategoryBind('^[3', DamType.ELECTRICITY, '3: elec'),
        CategoryBind('^[4', DamType.ASPHYXIATION, '4: asphy'),
        CategoryBind('^[5', DamType.ACID, '5: acid'),
        CategoryBind('^[6', DamType.POISON, '6: poison'),
        CategoryBind('^[7', DamType.COLD, '7: cold')
    ],
    [
        CategoryBind('^[!', OtherCategory.CHANNELLER_DRAIN, '1: drain'),
    ]
]

class State(NamedTuple):
    category: Category

state = State(DamType.MAGICAL)

def categoryBindHelp(selected: Category) -> str:
    getCatStr: Callable[[CategoryBind], str] = lambda cb: "*{0}*".format(cb.explanation) if cb.category == selected else cb.explanation

    return "\n".join(map(lambda cbs: " ".join(map(getCatStr, cbs)), CATEGORY_BINDS))

def changeDamType(category_raw: str):
    global state
    cat = category_raw.upper()
    selected = cast(Category, DamType[cat] if cat in DamType.__members__ else OtherCategory[cat])
    state = state._replace(category = selected)
    tfprint(categoryBindHelp(selected))

def setup():
    for key, category, explanation in flatten(CATEGORY_BINDS):
        eval("/def -i -q -b'{0}' = /python_call blaster.changeDamType {1}"
             .format(key, category.value))
    out("» Loaded blaster.py")

setup()