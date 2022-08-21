from typing import FrozenSet, Mapping, NamedTuple, Optional, Sequence

from utils import Color, NoValue


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


DAMTYPE_STR_TF: Mapping[Optional[DamType], str] = {
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

# https://www.99colors.net/color-names
def getDamtypeColor(damType: Optional[DamType]) -> Optional[Color]:
    if damType == DamType.ACID:
        return Color(0, 255, 0)  # green
    elif damType == DamType.ASPHYXIATION:
        return Color(202, 31, 123)  # magenta
    elif damType == DamType.COLD:
        return Color(0, 0, 255)  # blue
    elif damType == DamType.ELECTRICITY:
        return Color(125, 249, 255)  # electric blue
    elif damType == DamType.FIRE:
        return Color(226, 88, 34)  # flame
    elif damType == DamType.MAGICAL:
        return Color(255, 130, 67)  # mango tango
    elif damType == DamType.POISON:
        return Color(46, 139, 87)  # sea green
    elif damType == DamType.PSI:
        return Color(10, 186, 181)  # tiffany blue
    elif damType == DamType.HARM:
        return Color(139, 133, 137)  # taupe gray
    elif damType == DamType.PHYSICAL:
        return Color(192, 192, 192)  # silver
    elif damType == DamType.HEAL:
        return Color(253, 245, 230)  # old lace
    else:
        return None


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
        Spell(
            "prismatic burst",
            None,
            None,
            "",
            True,
            True,
        ),
        Spell(
            "acid blast",
            DamType.ACID,
            SpellType.MAGE_SINGLE_1,
            "fzz mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "acid ray",
            DamType.ACID,
            SpellType.MAGE_SINGLE_2,
            "fzz mar nak semen",
            True,
            True,
        ),
        Spell(
            "acid arrow",
            DamType.ACID,
            SpellType.MAGE_SINGLE_3,
            "fzz zur semen",
            True,
            True,
        ),
        Spell(
            "acid wind",
            DamType.ACID,
            SpellType.MAGE_SINGLE_4,
            "fzz zur sanc",
            True,
            True,
        ),
        Spell(
            "disruption",
            DamType.ACID,
            SpellType.MAGE_SINGLE_5,
            "fzz zur fehh",
            True,
            True,
        ),
        Spell(
            "acid storm",
            DamType.ACID,
            SpellType.MAGE_AREA_1,
            "fzz mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "acid rain",
            DamType.ACID,
            SpellType.MAGE_AREA_2,
            "fzz zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "acid shield",
            DamType.ACID,
            SpellType.MAGE_PROT_1,
            "hfizz hfizz nglurglptz",
            True,
            False,
        ),
        Spell(
            "corrosion shield",
            DamType.ACID,
            SpellType.MAGE_PROT_2,
            "sulphiraidzik hydrochloodriz gidz zuf",
            True,
            False,
        ),
        Spell(
            "blast vacuum",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_1,
            "ghht mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "strangulation",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_2,
            "ghht mar nak semen",
            True,
            True,
        ),
        Spell(
            "chaos bolt",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_3,
            "ghht zur semen",
            True,
            True,
        ),
        Spell(
            "suffocation",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_4,
            "ghht zur sanc",
            True,
            True,
        ),
        Spell(
            "vacuumbolt",
            DamType.ASPHYXIATION,
            SpellType.MAGE_SINGLE_5,
            "ghht zur fehh",
            True,
            True,
        ),
        Spell(
            "vacuum globe",
            DamType.ASPHYXIATION,
            SpellType.MAGE_AREA_1,
            "ghht mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "vacuum ball",
            DamType.ASPHYXIATION,
            SpellType.MAGE_AREA_2,
            "ghht zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "aura of wind",
            DamType.ASPHYXIATION,
            SpellType.MAGE_PROT_1,
            "englobo globo mc'pop",
            True,
            False,
        ),
        Spell(
            "ether boundary",
            DamType.ASPHYXIATION,
            SpellType.MAGE_PROT_2,
            "qor monoliftus",
            True,
            False,
        ),
        Spell(
            "cold ray",
            DamType.COLD,
            SpellType.MAGE_SINGLE_1,
            "cah mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "icebolt",
            DamType.COLD,
            SpellType.MAGE_SINGLE_2,
            "cah mar nak semen",
            True,
            True,
        ),
        Spell(
            "darkfire",
            DamType.COLD,
            SpellType.MAGE_SINGLE_3,
            "cah zur semen",
            True,
            True,
        ),
        Spell(
            "flaming ice",
            DamType.COLD,
            SpellType.MAGE_SINGLE_4,
            "cah zur sanc",
            True,
            True,
        ),
        Spell(
            "chill touch",
            DamType.COLD,
            SpellType.MAGE_SINGLE_5,
            "cah zur fehh",
            True,
            True,
        ),
        Spell(
            "hailstorm",
            DamType.COLD,
            SpellType.MAGE_AREA_1,
            "cah mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "cone of cold",
            DamType.COLD,
            SpellType.MAGE_AREA_2,
            "cah zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "frost shield",
            DamType.COLD,
            SpellType.MAGE_PROT_1,
            "nbarrimon zfettix roi",
            True,
            False,
        ),
        Spell(
            "frost insulation",
            DamType.COLD,
            SpellType.MAGE_PROT_2,
            "skaki barictos yetz fiil",
            True,
            False,
        ),
        Spell(
            "electrocution",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_1,
            "zot mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "forked lightning",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_2,
            "zot mar nak semen",
            True,
            True,
        ),
        Spell(
            "blast lightning",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_3,
            "zot zur semen",
            True,
            True,
        ),
        Spell(
            "lightning bolt",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_4,
            "zot zur sanc",
            True,
            True,
        ),
        Spell(
            "shocking grasp",
            DamType.ELECTRICITY,
            SpellType.MAGE_SINGLE_5,
            "zot zur fehh",
            True,
            True,
        ),
        Spell(
            "lightning storm",
            DamType.ELECTRICITY,
            SpellType.MAGE_AREA_1,
            "zot mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "chain lightning",
            DamType.ELECTRICITY,
            SpellType.MAGE_AREA_2,
            "zot zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "lightning shield",
            DamType.ELECTRICITY,
            SpellType.MAGE_PROT_1,
            "ohm",
            True,
            False,
        ),
        Spell(
            "energy channeling",
            DamType.ELECTRICITY,
            SpellType.MAGE_PROT_2,
            "kablaaaammmmm bliitz zundfer",
            True,
            False,
        ),
        Spell(
            "channelbolt",
            DamType.ELECTRICITY,
            SpellType.CHANNELLER_SINGLE,
            "tsaibaa",
            True,
            True,
        ),
        Spell(
            "lava blast",
            DamType.FIRE,
            SpellType.MAGE_SINGLE_1,
            "fah mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "meteor blast",
            DamType.FIRE,
            SpellType.MAGE_SINGLE_2,
            "fah mar nak semen",
            True,
            True,
        ),
        Spell(
            "fire blast",
            DamType.FIRE,
            SpellType.MAGE_SINGLE_3,
            "fah zur semen",
            True,
            True,
        ),
        Spell(
            "firebolt",
            DamType.FIRE,
            SpellType.MAGE_SINGLE_4,
            "fah zur sanc",
            True,
            True,
        ),
        Spell(
            "flame arrow",
            DamType.FIRE,
            SpellType.MAGE_SINGLE_5,
            "fah zur fehh",
            True,
            True,
        ),
        Spell(
            "lava storm",
            DamType.FIRE,
            SpellType.MAGE_AREA_1,
            "fah mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "meteor swarm",
            DamType.FIRE,
            SpellType.MAGE_AREA_2,
            "fah zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "flame shield",
            DamType.FIRE,
            SpellType.MAGE_PROT_1,
            "huppa huppa tiki tiki",
            True,
            False,
        ),
        Spell(
            "heat reduction",
            DamType.FIRE,
            SpellType.MAGE_PROT_2,
            "hot hot not zeis daimons",
            True,
            False,
        ),
        Spell(
            "channelburn",
            DamType.FIRE,
            SpellType.CHANNELLER_SINGLE,
            "grhagrhagrhagrah gra gra Hyaa!",
            True,
            True,
        ),
        Spell(
            "golden arrow",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_1,
            "gtzt mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "summon greater spores",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_2,
            "gtzt mar nak semen",
            True,
            True,
        ),
        Spell(
            "levin bolt",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_3,
            "gtzt zur semen",
            True,
            True,
        ),
        Spell(
            "summon lesser spores",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_4,
            "gtzt zur sanc",
            True,
            True,
        ),
        Spell(
            "magic missile",
            DamType.MAGICAL,
            SpellType.MAGE_SINGLE_5,
            "gtzt zur fehh",
            True,
            True,
        ),
        Spell(
            "magic eruption",
            DamType.MAGICAL,
            SpellType.MAGE_AREA_1,
            "gtzt mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "magic wave",
            DamType.MAGICAL,
            SpellType.MAGE_AREA_2,
            "gtzt zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "repulsor aura",
            DamType.MAGICAL,
            SpellType.MAGE_PROT_1,
            "shamarubu incixtes delfo",
            True,
            False,
        ),
        Spell(
            "magic dispersion",
            DamType.MAGICAL,
            SpellType.MAGE_PROT_2,
            "meke tul magic",
            True,
            False,
        ),
        Spell(
            "channelball",
            DamType.MAGICAL,
            SpellType.CHANNELLER_SINGLE,
            "shar ryo den...Haa!",
            True,
            True,
        ),
        Spell(
            "summon carnal spores",
            DamType.POISON,
            SpellType.MAGE_SINGLE_1,
            "krkx mar nak grttzt",
            True,
            True,
        ),
        Spell(
            "power blast",
            DamType.POISON,
            SpellType.MAGE_SINGLE_2,
            "krkx mar nak semen",
            True,
            True,
        ),
        Spell(
            "venom strike",
            DamType.POISON,
            SpellType.MAGE_SINGLE_3,
            "krkx zur semen",
            True,
            True,
        ),
        Spell(
            "poison blast",
            DamType.POISON,
            SpellType.MAGE_SINGLE_4,
            "krkx zur sanc",
            True,
            True,
        ),
        Spell(
            "thorn spray",
            DamType.POISON,
            SpellType.MAGE_SINGLE_5,
            "krkx zur fehh",
            True,
            True,
        ),
        Spell(
            "killing cloud",
            DamType.POISON,
            SpellType.MAGE_AREA_1,
            "krkx mar nak grttzt gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "poison spray",
            DamType.POISON,
            SpellType.MAGE_AREA_2,
            "krkx zur semen gnatlnamauch",
            True,
            True,
        ),
        Spell(
            "shield of detoxification",
            DamType.POISON,
            SpellType.MAGE_PROT_1,
            "nyiaha llaimay exchekes ployp",
            True,
            False,
        ),
        Spell(
            "toxic dilution",
            DamType.POISON,
            SpellType.MAGE_PROT_2,
            "morri nam pantoloosa",
            True,
            True,
        ),
        Spell(
            "armour of aether",
            DamType.PHYSICAL,
            SpellType.MAGE_PROT_1,
            "fooharribah inaminos cantor",
            True,
            False,
        ),
        Spell(
            "force absorption",
            DamType.PHYSICAL,
            SpellType.MAGE_PROT_2,
            "ztonez des deckers",
            True,
            False,
        ),
        Spell("channelspray", None, None, "grinurb sdan imflagrum", True, True),
        Spell("displacement", None, None, "diiiiuuunz aaanziz", True, False),
        Spell("blurred image", None, None, "ziiiuuuuns wiz", True, False),
        Spell("shield of protection", None, None, "nsiiznau", True, False),
        Spell("iron will", None, None, "", True, False),
        Spell("floating", None, None, "", True, False),
        Spell("drain enemy", None, None, "enfuego delvivendo", True, True),
        Spell(
            "dispel magical protection", None, None, "removezzzzzarmour", True, False
        ),
        Spell("resist dispel", None, None, "zicks laai qluu", True, False),
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
        Spell("deaths door", None, None, "mumbo jumbo", True, False),
        Spell("runic heal", None, None, "!* *", True, False),
        Spell("remove poison", None, None, "judicandus saugaiii", True, False),
        Spell("cure player", None, None, "freudemas egoid", True, False),
        Spell("restore", None, None, "Siwa on selvaa saastoa.", True, False),
        Spell(
            "natural renewal",
            None,
            None,
            "Naturallis Judicandus Imellys",
            True,
            False,
        ),
        Spell("unpain", None, None, "harnaxan temnahecne", True, False),
        Spell("unstun", None, None, "Paxus", True, False),
        Spell("earth power", None, None, "", True, False),
        Spell("flex shield", None, None, "", True, False),
        Spell("earth skin", None, None, "", True, False),
        Spell("vine mantle", None, None, "", True, False),
        Spell("water walking", None, None, "", True, False),
        Spell("blessing of tarmalen", None, None, "", True, False),
        Spell("regeneration", None, None, "", True, False),
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
