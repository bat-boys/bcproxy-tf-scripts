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
    HEAL = "heal"


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
    DamType.HEAL: "@{BCwhite}" + "{:4}".format(DamType.HEAL.value[:4]) + "@{n}",
    None: "    ",
}


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
        Spell("dispel magical protection", None, None, "", True, False),
        Spell("resist dispel", None, None, "", True, False),
        # tarmalen
        Spell(
            "cure light wounds", DamType.HEAL, None, "judicandus mercuree", True, False
        ),
        Spell(
            "cure serious wounds", DamType.HEAL, None, "judicandus ignius", True, False
        ),
        Spell(
            "cure critical wounds",
            DamType.HEAL,
            None,
            "judicandus mangenic",
            True,
            False,
        ),
        Spell("minor heal", DamType.HEAL, None, "judicandus pzarcumus", True, False),
        Spell("major heal", DamType.HEAL, None, "judicandus pafzarmus", True, False),
        Spell("true heal", DamType.HEAL, None, "judicandus zapracus", True, False),
        Spell("deaths door", DamType.HEAL, None, "mumbo jumbo", True, False),
        Spell("runic heal", DamType.HEAL, None, "!* *", True, False),
        Spell("remove poison", DamType.HEAL, None, "judicandus saugaiii", True, False),
        Spell("cure player", DamType.HEAL, None, "freudemas egoid", True, False),
        Spell("restore", DamType.HEAL, None, "Siwa on selvaa saastoa.", True, False),
        Spell(
            "natural renewal",
            DamType.HEAL,
            None,
            "Naturallis Judicandus Imellys",
            True,
            False,
        ),
        Spell("heal body", DamType.HEAL, None, "ZAP ZAP ZAP!", True, False),
        Spell(
            "minor party heal",
            DamType.HEAL,
            None,
            "judicandus puorgo ignius",
            False,
            True,
        ),
        Spell(
            "major party heal",
            DamType.HEAL,
            None,
            "judicandus puorgo mangenic",
            False,
            True,
        ),
        Spell(
            "true party heal",
            DamType.HEAL,
            None,
            "judicandus eurto mangenic",
            False,
            True,
        ),
        Spell(
            "unpain",
            None,
            None,
            "harnaxan temnahecne",
            True,
            False,
        ),
        Spell(
            "unstun",
            None,
            None,
            "Paxus",
            True,
            False,
        ),
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
