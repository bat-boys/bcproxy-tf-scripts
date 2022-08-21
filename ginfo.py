from copy import deepcopy
from re import compile as reCompile
from tf import eval as tfeval  # type: ignore
from typing import Mapping, NamedTuple, Optional, Sequence, Set

from spells import DamType
from tfutils import tfprint
from utils import strtoi


MAGE = reCompile("(:?Mage|Triad) \((?P<subguilds>.+)\)")
MAGE_TYPES = reCompile("^(?P<type>.+?)(?: \[(?P<lvl>\d+)\])?$")
GUILD_WITH_LEVELS = reCompile("(?P<guild>.+) \((?P<lvl>\d+)(?:/(?P<maxlvl>\d+))?\)")

GUILD_ORDER = [
    "Disciple",
    # magical
    "Riftwalker",
    "Channellers",
    "Psionicist",
    "Mage",
    "Asphyxiation",
    "Acid",
    "Cold",
    "Electricity",
    "Fire",
    "Magical",
    "Poison",
    "Inner circle",
    # civilized
    "Merchant",
    "Alchemists",
    "Sabres",
    "Runemages",
    "Folklorist",
    "Bard",
    "Civmage",
    "Knight",
    # civfight puuttuu
    # evil religious
    "Tzarakk",
    "Nergal",
    "Reaver",
    "Priests",
    "Triad",
    "Curate",
    "Seminary",
    # good religious
    "Monk",
    "Templar",
    "Liberator",
    "Animist",
    "Tarmalen",
    "Druids",
    "Nun",
    # nomad
    "Crimson",
    "Archers",
    "Ranger",
    "Barbarian",
    "Beastmaster",
    # multi
    "Kharim",
    "Squire",
    "Cavalier",
    "Navigator",
    "Explorer",
    "Treenav",
]

HIDE_GUILDS = set(["Society levels"])

GUILD_SHORTHAND = {
    "Disciple": "discip",
    # magical
    "Riftwalker": "rift",
    "Channellers": "channu",
    "Psionicist": "psi",
    "Mage": "mage",
    "Asphyxiation": "asphy",
    "Acid": "acid",
    "Cold": "cold",
    "Electricity": "elec",
    "Fire": "fire",
    "Magical": "mana",
    "Poison": "pois",
    "Inner circle": "inner",
    # civilized
    "Merchant": "merch",
    "Alchemists": "alch",
    "Sabres": "sabre",
    "Runemages": "rune",
    "Folklorist": "folk",
    "Bard": "bard",
    "Civmage": "civmage",
    "Knight": "knight",
    # evil religious
    "Tzarakk": "tzarakk",
    "Nergal": "nergal",
    "Reaver": "reaver",
    "Priests": "priest",
    "Triad": "triad",
    "Curate": "curate",
    "Seminary": "seminary",
    # good religious
    "Monk": "monk",
    "Templar": "templa",
    "Liberator": "libre",
    "Animist": "animist",
    "Tarmalen": "tarma",
    "Druids": "druid",
    "Nun": "nun",
    # nomad
    "Crimson": "crimso",
    "Archers": "archer",
    "Ranger": "ranger",
    "Barbarian": "barb",
    "Beastmaster": "bmaster",
    # multi
    "Kharim": "kharim",
    "Squire": "squire",
    "Cavalier": "cava",
    "Navigator": "nav",
    "Explorer": "explorer",
    "Treenav": "treenav",
}

BG_SHORTHAND = {
    "Good religious": "grelig",
    "Evil religious": "erelig",
    "Magical": "magical",
    "Civilized": "civ",
    "Nomad": "nomad",
}


class PlayerGuild(NamedTuple):
    guild: str
    lvl: Optional[int]
    maxlvl: Optional[int]


class State(NamedTuple):
    player: Optional[str]
    guilds: Set[PlayerGuild]
    background: Optional[str]
    partyReport: bool
    playersLeft: Sequence[str]
    country: Optional[str]
    level: Optional[str]
    race: Optional[str]
    birth: Optional[str]


state = State(None, set(), None, False, list(), None, None, None, None)


def start(s: str):
    global state
    state = state._replace(player=s[:-1])
    # n15 = maximum of 15 matches, don't match everything if end doesn't work
    tfeval(
        "/def -i -p1 -n15 -ag -mglob -t`\*` ginfo_guild = /python_call ginfo.guild \%\*"
    )


def end(s: str):
    global state
    state = state._replace(background=s)
    tfeval("/undef ginfo_guild")
    if state.partyReport:
        tfeval("@party report {0}".format(toString()))
    else:
        tfprint(toString())
    cleanup("")


def hidden(s: str):
    global state
    country = state.country if state.country is not None else "unknown country"
    msg = "{0}: hidden, {1}".format(s, country)
    if state.partyReport:
        tfeval("@party report {0}".format(msg))
    else:
        tfprint(msg)
    cleanup("")


def guild(s: str):
    global state
    mage = MAGE.match(s)
    guildWithLevels = GUILD_WITH_LEVELS.match(s)
    if mage and mage.group("subguilds") != "10/10":
        for typeStr in mage.group("subguilds").split(", "):
            type = MAGE_TYPES.match(typeStr)
            if type:
                lvl = (
                    strtoi(type.group("lvl")) if type.group("lvl") is not None else None
                )
                state.guilds.add(PlayerGuild(type.group("type"), lvl, 10))
    elif guildWithLevels:
        lvl2 = guildWithLevels.group("lvl")
        maxlvl = guildWithLevels.group("maxlvl")
        state.guilds.add(
            PlayerGuild(
                guildWithLevels.group("guild"),
                strtoi(lvl2),
                strtoi(maxlvl) if maxlvl is not None else None,
            )
        )
    else:
        state.guilds.add(PlayerGuild(s, None, None))


def pgToString(pg: PlayerGuild) -> str:
    guild = GUILD_SHORTHAND[pg.guild] if pg.guild in GUILD_SHORTHAND else pg.guild
    if pg.lvl is None or pg.maxlvl is None or pg.lvl == pg.maxlvl:
        return guild
    else:
        return "{0}({1})".format(guild, pg.lvl)


def sortNumber(pg: PlayerGuild) -> int:
    if pg.lvl is None or pg.maxlvl is None or pg.lvl == pg.maxlvl:
        if pg.guild in GUILD_ORDER:
            return 100 + list(reversed(GUILD_ORDER)).index(pg.guild)
        else:
            return 0
    else:
        return pg.lvl


def toString() -> str:
    global state
    nonHiddenGuilds = filter(lambda pg: not pg.guild in HIDE_GUILDS, state.guilds)
    guilds = sorted(nonHiddenGuilds, key=lambda pg: sortNumber(pg), reverse=True)
    guildsStrs = map(lambda pg: pgToString(pg), guilds)
    country = state.country if state.country is not None else "unknown country"

    if state.player is not None and state.background is not None:
        openBrace = "["
        closeBrace = "]"
        if (
            state.birth == "elder"
            or state.birth == "ancient"
            or state.birth == "eternal"
        ):
            openBrace = "("
            closeBrace = ")"
        return "{0} {6}{1}{7}: {2} {3} {4}, {5}".format(
            state.player,
            state.level,
            "-".join(guildsStrs),
            BG_SHORTHAND[state.background],
            state.race,
            country,
            openBrace,
            closeBrace,
        )
    else:
        return ""


def countries(country: Optional[str]):
    global state
    state = state._replace(country=(country[1:-2] if country is not None else None))


def nextPlayer():
    global state
    player = state.playersLeft.pop(0)
    player = player[:1].upper() + player[1:].lower()
    tfeval(
        "/def -i -p10 -ag -mglob -t`"
        + "{0} has registered to be from '*'.".format(player)
        + "` ginfo_countries_registered = /python_call ginfo.countries \%-6"
    )
    tfeval(
        "/def -i -p10 -ag -mglob -t`"
        + "{0} is logged in from '*'.".format(player)
        + "` ginfo_countries_logged = /python_call ginfo.countries \%-5"
    )
    tfeval(
        "/def -i -p10 -ag -msimple -t`"
        + "The country information for {0} is not accessible currently.".format(player)
        + "` ginfo_countries_not_accessible"
    )
    tfeval(
        "/def -i -p10 -ag -msimple -t`"
        + "No country information available for {0}.".format(player)
        + "` ginfo_countries_no_information"
    )
    tfeval("/def -i -p10 -ag -msimple -t`` ginfo_countries_extra_linefeed")
    tfeval(
        "/def -i -ag -p10 -n1 -mregexp -t`"
        + "is a level +([a-zA-Z0-9]+) (.+?)(?: player killer)? of the ([A-Z][a-z]+) race."
        + "` ginfo_finger = /python_call ginfo.fingerLevel \%P1 \%P2 \%P3"
    )
    tfeval('@grep "is a level" finger {0}'.format(player))
    tfeval("@countries {0}".format(player))
    tfeval("@ginfo {0}".format(player))


def cleanup(s: str):
    global state
    state = state._replace(player=None, guilds=set(), background=None, country=None)
    tfeval("/undef ginfo_countries_registered")
    tfeval("/undef ginfo_countries_logged")
    tfeval("/undef ginfo_countries_not_accessible")
    tfeval("/undef ginfo_countries_no_information")
    tfeval("/undef ginfo_countries_extra_linefeed")
    if len(state.playersLeft) != 0:
        nextPlayer()
    else:
        state = state._replace(partyReport=False)
        tfeval("/edit -c0 ginfo_start")
        tfeval("/edit -c0 ginfo_end")
        tfeval("/edit -c0 ginfo_hidden")
        tfeval("/edit -c0 ginfo_no_such_player")


def ginfo(players: str):
    global state
    state = state._replace(playersLeft=players.split(" "))
    tfeval("/edit -c100 ginfo_start")
    tfeval("/edit -c100 ginfo_end")
    tfeval("/edit -c100 ginfo_hidden")
    tfeval("/edit -c100 ginfo_no_such_player")
    nextPlayer()


def fingerLevel(s: str):
    global state
    [level, birth, race] = s.split()
    state = state._replace(level=level, birth=birth, race=race.lower())


def finger(player: str):
    ginfo(player)
    tfeval("@finger {0}".format(player))


def partyReport(players: str):
    global state
    state = state._replace(partyReport=True)
    ginfo(players)


whoState: Set[str] = set()


def who(params: str):
    global whoState
    whoState = set()
    tfeval(
        "/def -i -p10 -ag -n9 -mregexp -t`^[\\[({]........... ([A-Za-z]+)` ginfo_who = /python_call ginfo.whoAddPlayer \%P1"
    )
    tfeval(
        "/def -i -p10 -ag -mregexp -t`^[0-9]+ players shown.` ginfo_who_end = /python_call ginfo.whoEnd"
    )
    tfeval("@who {0}".format(params))


def whoAddPlayer(player: str):
    global whoState
    whoState.add(player)


def whoEnd(opts: str):
    global whoState
    tfeval("/undef ginfo_who")
    tfeval("/undef ginfo_who_end")
    if len(whoState) > 0:
        ginfo(" ".join(whoState))


def setup():
    cmds = [
        "/def -i -p10 -c0 -ag -mglob -t`Guild information for *` ginfo_start = /python_call ginfo.start \%-3",
        "/def -i -p10 -c0 -ag -mglob -t`Background: *` ginfo_end = /python_call ginfo.end \%-1",
        "/def -i -p10 -c0 -ag -mglob -t`* has chosen to hide their guild information.` ginfo_hidden = /python_call ginfo.hidden \%1",
        "/def -i -p10 -c0 -ag -mglob -t`No such player (*).` ginfo_no_such_player",
        "/def -i -p10 -c0 -ag -mglob -t`* does not seem to have any guild information (offline).` ginfo_hidden2 = /python_call ginfo.hidden \%1",
        "/def ginfo = /python_call ginfo.ginfo \%*",
        "/def giwho = /python_call ginfo.who \%*",
        "/def pwho = /python_call ginfo.who party \%*",
    ]

    for cmd in cmds:
        tfeval(cmd)

    tfprint("Loaded ginfo.py")


setup()
