from enum import Enum
from typing import FrozenSet, Mapping, NamedTuple, Optional, Sequence

from utils import NoValue, tfprint


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
    PROT = "prot"
    UTILITY = "utility"


class Spell(NamedTuple):
    name: str
    damType: Optional[DamType]
    spellType: Optional[SpellType]
    vocals: str
    withTarget: bool
    withoutTarget: bool


SPELLS: FrozenSet[Spell] = frozenset(
    [
        Spell("acid blast", DamType.ACID, SpellType.MAGE_SINGLE_1, "", True, True),
        Spell("acid ray", DamType.ACID, SpellType.MAGE_SINGLE_2, "", True, True),
        Spell("acid arrow", DamType.ACID, SpellType.MAGE_SINGLE_3, "", True, True),
        Spell("acid wind", DamType.ACID, SpellType.MAGE_SINGLE_4, "", True, True),
        Spell("disruption", DamType.ACID, SpellType.MAGE_SINGLE_5, "", True, True),
        Spell("acid storm", DamType.ACID, SpellType.MAGE_AREA_1, "", True, True),
        Spell("acid rain", DamType.ACID, SpellType.MAGE_AREA_2, "", True, True),
        Spell("acid shield", DamType.ACID, SpellType.MAGE_PROT_1, "", True, False),
        Spell("corrosion shield", DamType.ACID, SpellType.MAGE_PROT_2, "", True, False),
        Spell(
            "blast vacuum",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_1,
            "",
            True,
            True,
        ),
        Spell(
            "strangulation",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_2,
            "",
            True,
            True,
        ),
        Spell(
            "chaos bolt", DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_3, "", True, True
        ),
        Spell(
            "suffocation", DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_4, "", True, True
        ),
        Spell(
            "vacuumbolt", DamType.ASPHYXIATION, SpellType.MAGE_SINGLE_5, "", True, True
        ),
        Spell(
            "vacuum globe", DamType.ASPHYXIATION, SpellType.MAGE_AREA_1, "", True, True
        ),
        Spell(
            "vacuum ball", DamType.ASPHYXIATION, SpellType.MAGE_AREA_2, "", True, True
        ),
        Spell(
            "aura of wind", DamType.ASPHYXIATION, SpellType.MAGE_PROT_1, "", True, False
        ),
        Spell(
            "ether boundary",
            DamType.ASPHYXIATION,
            SpellType.MAGE_PROT_2,
            "",
            True,
            False,
        ),
        Spell("cold ray", DamType.COLD, SpellType.MAGE_SINGLE_1, "", True, True),
        Spell("icebolt", DamType.COLD, SpellType.MAGE_SINGLE_2, "", True, True),
        Spell("darkfire", DamType.COLD, SpellType.MAGE_SINGLE_3, "", True, True),
        Spell("flaming ice", DamType.COLD, SpellType.MAGE_SINGLE_4, "", True, True),
        Spell("chill touch", DamType.COLD, SpellType.MAGE_SINGLE_5, "", True, True),
        Spell("hailstorm", DamType.COLD, SpellType.MAGE_AREA_1, "", True, True),
        Spell("cone of cold", DamType.COLD, SpellType.MAGE_AREA_2, "", True, True),
        Spell("frost shield", DamType.COLD, SpellType.MAGE_PROT_1, "", True, False),
        Spell("frost insulation", DamType.COLD, SpellType.MAGE_PROT_2, "", True, False),
        Spell(
            "electrocution",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_1,
            "",
            True,
            True,
        ),
        Spell(
            "forked lightning",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_2,
            "",
            True,
            True,
        ),
        Spell(
            "blast lightning",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_3,
            "",
            True,
            True,
        ),
        Spell(
            "lightning bolt",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_4,
            "",
            True,
            True,
        ),
        Spell(
            "shocking grasp",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_5,
            "",
            True,
            True,
        ),
        Spell(
            "lightning storm",
            DamType.ELECTRICITY,
            SpellType.MAGE_AREA_1,
            "",
            True,
            True,
        ),
        Spell(
            "chain lightning",
            DamType.ELECTRICITY,
            SpellType.MAGE_AREA_2,
            "",
            True,
            True,
        ),
        Spell(
            "lightning shield",
            DamType.ELECTRICITY,
            SpellType.MAGE_PROT_1,
            "",
            True,
            False,
        ),
        Spell(
            "energy channeling",
            DamType.ELECTRICITY,
            SpellType.MAGE_PROT_2,
            "",
            True,
            False,
        ),
        Spell(
            "channelbolt",
            DamType.ELECTRICITY,
            SpellType.CHANNELLER_SINGLE,
            "",
            True,
            True,
        ),
        Spell("lava blast", DamType.FIRE, SpellType.MAGE_SINGLE_1, "", True, True),
        Spell("meteor blast", DamType.FIRE, SpellType.MAGE_SINGLE_2, "", True, True),
        Spell("fire blast", DamType.FIRE, SpellType.MAGE_SINGLE_3, "", True, True),
        Spell("firebolt", DamType.FIRE, SpellType.MAGE_SINGLE_4, "", True, True),
        Spell("flame arrow", DamType.FIRE, SpellType.MAGE_SINGLE_5, "", True, True),
        Spell("lava storm", DamType.FIRE, SpellType.MAGE_AREA_1, "", True, True),
        Spell("meteor swarm", DamType.FIRE, SpellType.MAGE_AREA_2, "", True, True),
        Spell("flame shield", DamType.FIRE, SpellType.MAGE_PROT_1, "", True, False),
        Spell("heat reduction", DamType.FIRE, SpellType.MAGE_PROT_2, "", True, False),
        Spell("channelburn", DamType.FIRE, SpellType.CHANNELLER_SINGLE, "", True, True),
        Spell("golden arrow", DamType.MAGICAL, SpellType.MAGE_SINGLE_1, "", True, True),
        Spell(
            "summon greater spores",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_2,
            "",
            True,
            True,
        ),
        Spell("levin bolt", DamType.MAGICAL, SpellType.MAGE_SINGLE_3, "", True, True),
        Spell(
            "summon lesser spores",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_4,
            "",
            True,
            True,
        ),
        Spell(
            "magic missile", DamType.MAGICAL, SpellType.MAGE_SINGLE_5, "", True, True
        ),
        Spell("magic eruption", DamType.MAGICAL, SpellType.MAGE_AREA_1, "", True, True),
        Spell("magic wave", DamType.MAGICAL, SpellType.MAGE_AREA_2, "", True, True),
        Spell("repulsor aura", DamType.MAGICAL, SpellType.MAGE_PROT_1, "", True, False),
        Spell(
            "magic dispersion", DamType.MAGICAL, SpellType.MAGE_PROT_2, "", True, False
        ),
        Spell(
            "channelball", DamType.MAGICAL, SpellType.CHANNELLER_SINGLE, "", True, True
        ),
        Spell(
            "summon carnal spores",
            DamType.POISON,
            SpellType.MAGE_SINGLE_1,
            "",
            True,
            True,
        ),
        Spell("power blast", DamType.POISON, SpellType.MAGE_SINGLE_2, "", True, True),
        Spell("venom strike", DamType.POISON, SpellType.MAGE_SINGLE_3, "", True, True),
        Spell("poison blast", DamType.POISON, SpellType.MAGE_SINGLE_4, "", True, True),
        Spell("thorn spray", DamType.POISON, SpellType.MAGE_SINGLE_5, "", True, True),
        Spell("killing cloud", DamType.POISON, SpellType.MAGE_AREA_1, "", True, True),
        Spell("poison spray", DamType.POISON, SpellType.MAGE_AREA_2, "", True, True),
        Spell(
            "shield of detoxification",
            DamType.POISON,
            SpellType.MAGE_PROT_1,
            "",
            True,
            False,
        ),
        Spell("toxic dilution", DamType.POISON, SpellType.MAGE_PROT_2, "", True, True),
        Spell(
            "armour of aether", DamType.PHYSICAL, SpellType.MAGE_PROT_1, "", True, False
        ),
        Spell(
            "force absorption", DamType.PHYSICAL, SpellType.MAGE_PROT_2, "", True, False
        ),
        Spell("channelspray", None, None, "", True, True),
        Spell("displacement", None, None, "", True, False),
        Spell("blurred image", None, None, "", True, False),
        Spell("shield of protection", None, None, "", True, False),
        Spell("drain enemy", None, None, "", True, True),
    ]
)


def getSpellByType(damType: DamType, spellType: SpellType) -> Optional[Spell]:
    for spell in SPELLS:
        if spell.damType == damType and spell.spellType == spellType:
            return spell
    return None


def getSpellByName(name: str) -> Optional[Spell]:
    for spell in SPELLS:
        if spell.name == name:
            return spell
    return None
