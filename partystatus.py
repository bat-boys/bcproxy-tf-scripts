import tf
import re
import json

#: Keybinds for member targetting
#:
#: This is in format [y][x] so that it is visually correct
#: and indexes starting from 1 so that we can use the same numbers as batmud
#: (hence Nones in index 0)
#:
#: These default bindings are ALT-7, ALT-U, etc.
PLACE_KEYBINDS = [
    None,
    [None, '^[7', '^[8', '^[9', '^[0'],
    [None, '^[u', '^[i', '^[o', '^[p'],
    [None, '^[j', '^[k', '^[l', '^[ö']
]

SETUP_COMMANDS = [
    # setup statusbar
    "/set status_pad= ",
    "/set status_height=6",

    # disable ggrtf status updates
    "/def -i gprots_update = /return",
    "/def -i gstatus_update = /return",
    "/def -i gstatus_update_do = /return",

    # for hiding def lines when places change
    "/def -aLg -c0 -h'REDEF' gag_redef",

    # grab bcproxy party status update message
    "/def -mglob -F -q -t'∴party *' bcproxy_party = /python_call partystatus.trigger_party_message \%-1",

    # /t <target> to manually change targets
    "/def t = /python_call partystatus.trigger_target_changed %1",

    # pss: nergal minion in front row, WIP
    '/def -i -F -p999 -mregexp -t`' +
    '^\\\|(.)([1-3?])\\\.([1-3?])  ' + # idle, y, x
    '\\\+([A-Za-z ]+) +' + # name {12}
    '([a-z]+) +' + # state
    '([0-9]+)\\\(([0-9]+)\\\) +' + # hp / hpmax
    '([A-Za-z .]+?)  +' + # sp
    '([A-Za-z .]+) ' + # ep
    '\\\| [?][?][?] \\\|              \\\|\$' +
    '` pss_nergal = /python_call partystatus.trigger_nergal_frontrow "' +
    "{ 'y': \%P1, 'x': \%P2, 'name': '\%P3', 'state': '\%P4', 'hp': \%P5, " +
    "'hpmax': \%P6, 'sp': '\%P7', 'ep': '\%P8' }" +
    '"'
]

#: Batclient party status update message (62) fields
PARTY_STATUS_UPDATE_FIELDS = [
    'player',
    'race',
    'gender',
    'level',
    'hp',
    'maxhp',
    'sp',
    'maxsp',
    'ep',
    'maxep',
    'party_name',
    'place_x',
    'place_y',
    'creator',
    'formation',
    'member',
    'entry',
    'following',
    'leader',
    'linkdead',
    'resting',
    'idle',
    'invisible',
    'dead',
    'stunned',
    'unconscious',
    'party_exp',
    'total_party_exp',
    'party_length_in_seconds',
    'party_creation_time'
]

#: Latest status update data for each member
bcproxy_stats = {}

#: PSS data for each member, WIP
pss_stats = {}

#: Places for members
#:
#: Used like member_places[y][x] = player
#:
#: And indexes starting from 1 like in PLACE_KEYBINDS.
member_places = [
    None,
    [None, None, None, None, None],
    [None, None, None, None, None],
    [None, None, None, None, None]
]

#: Previous place for each member
#:
#: This is used for saving member's place in the status area when
#: a member goes out of formation.
previous_places = {}

#: Other state
#:
#: Apparently global string variables don't work correctly, so use
#: a dictionary for storing cast target.
#:
#: Probably something to do with pass-by-value vs pass-by-reference?
other_state = {
    'cast_target': None
}

def parse_message(message):
    """
    Parse incoming party update message

    :param message: message as a string with fields separated by spaces
    :returns: dictionary with fields and their respective values
              boolean and number fields are converted to respective
              python data types
    """
    d = dict(zip(PARTY_STATUS_UPDATE_FIELDS, message.split(' ')))

    for field in ['level', 'hp', 'maxhp', 'sp', 'maxsp', 'ep',
                  'maxep', 'place_x', 'place_y', 'unconscious',
                  'stunned']:
        d[field] = int(d[field])

    for field in ['formation', 'member', 'entry', 'following', 'leader',
                  'linkdead', 'resting', 'idle', 'invisible', 'dead']:
        d[field] = d[field] == '1'

    # previously set cast target
    d['cast_target'] = d['player'] == other_state['cast_target']

    return d

def update_status():
    """
    Update tf status area

    Uses tf command /status_add
    """
    for i in range(0, 3):
        col1 = status_lines(1, i + 1)
        col2 = status_lines(2, i + 1)
        col3 = status_lines(3, i + 1)
        col4 = status_lines(4, i + 1)

        tf.eval("/status_add -c -r{0} {1} {2} {3} {4}"
                .format(i * 2, col1[0], col2[0], col3[0], col4[0]))
        tf.eval("/status_add -c -r{0} {1} {2} {3} {4}"
                .format(i * 2 + 1, col1[1], col2[1], col3[1], col4[1]))

def status_lines(x, y):
    """
    For given member place, get the tf status line strings (two lines per member)

    <player name> <hp>/<hpmax> <hpdiff to max>
    <player state> <ep> <sp>/<spmax> <* if player is cast target>

    For example:
         Ruska  408/ 445  -37
      ldr  224 1404/1404

    :param x: member place x coordinate
    :param y: member place y coordinate
    :returns: Tuple of two strings for tf status lines
    """
    try:
        stats = bcproxy_stats[member_places[y][x]]
        hpdiff = stats['hp'] - stats['maxhp']
        state = member_state(stats)

        return [
            "'{0}':-9:{1} '{2}':-5:{4} '/' '{3}':-4 '{5}':-5:Crgb511".format(
                stats['player'][: 8],
                member_name_color(stats),
                stats['hp'],
                stats['maxhp'],
                green_red_gradient(stats['hp'], stats['maxhp'], 200, 0.2),
                hpdiff or ' '
            ),
            "'{0}':-5:{1} '{2}':-4 '{3}':-5 '/' '{4}':-4 {5}".format(
                state[0],
                state[1],
                stats['ep'],
                stats['sp'],
                stats['maxsp'],
                "' *':5:BCrgb551" if stats['cast_target'] else "'':5"
            )]
    # if member_places[y][x] is None, there is no player in that place,
    # so clear that spot in status bar
    except KeyError as e:
        return ["'                        '", "'                        '"]
    except IndexError as e:
        return ["'                        '", "'                        '"]

def member_state(stats):
    """
    String and color for member state
    """
    # ambushed is missing as batmud gives that in pss but not in the party
    # status message for batclient
    if stats['unconscious'] == 1:
        return ["unc", 'BCrgb500']
    if stats['unconscious'] > 1:
        return ["unc|{0}".format(str(stats['unconscious'] - 2)), 'BCrgb500']
    if stats['stunned'] > 0:
        return ["stu|{0}".format(str(stats['stunned'])), 'BCrgb500']

    if stats['linkdead']:
        return ['ld', '']
    if stats['dead']:
        return ['dead', '']
    if stats['resting']:
        return ['rest', '']

    if stats['invisible']:
        return ['invis', '']
    if stats['formation']:
        return ['form', '']
    if stats['member']:
        return ['mbr', '']
    if stats['entry']:
        return ['', '']
    if stats['following']:
        return ['fol', '']
    if stats['leader']:
        return ['ldr', '']

    return ['unk', 'Crgb500']

def member_name_color(stats):
    if stats['unconscious'] or stats['stunned']:
        return 'BCrgb500'
    if stats['member']:
        return 'Crgb435'
    if stats['linkdead'] or stats['idle'] or stats['formation'] or stats['resting'] \
       or stats['dead']:
        return ''
    return 'BCrgb555'

def green_red_gradient(n, n_max, all_red_abs, all_red_ratio):
    all_red = max(all_red_abs, int(n_max * all_red_ratio + 0.5))

    if n < all_red:
        return "BCrgb500"
    if n >= n_max:
        return "BCrgb050"

    # http://stackoverflow.com/a/340245
    # green is 0 and red 1, so invert the ratio to get maximum to be green
    # also, bottom 10% is already handled, so reduce 10% of maximum from both
    n_ratio = 1 - ((n - all_red) / (n_max - all_red))
    r = int(5 * n_ratio + 0.5)
    g = int(5 * (1 - n_ratio) + 0.5)
    return "Crgb{0}{1}0".format(r, g)

def clear_member_places():
    for x in range(1, 5):
        for y in range(1, 4):
            member_places[y][x] = None

def update_places():
    clear_member_places()

    for player in list(bcproxy_stats):
        x = bcproxy_stats[player]['place_x']
        y = bcproxy_stats[player]['place_y']

        # new player in party
        if not player in previous_places:
            place_changed(player, x, y)
        elif previous_places[player] != [x, y]:
            prev_x = previous_places[player][0]
            prev_y = previous_places[player][1]
            # if the previous slot is empty, leave player there
            # if someone else is there that is not yet looped, it
            # will override this
            if (x > 3 or y > 3) and member_places[prev_y][prev_x] == None:
                x = prev_x
                y = prev_y
            else:
                place_changed(player, x, y)

        previous_places[player] = [x, y]
        try:
            member_places[y][x] = player
        except IndexError as e:
            continue

def place_changed(player, x, y):
    tf.out("place changed {0}, x: {1} y: {2}".format(player, x, y))
    if x >= 1 and x <= 3 and y >= 1 and y <= 3:
        tf.eval("/edit -c100 gag_redef")
        tf.eval("/def -i -q -b'{0}' = /python_call partystatus.trigger_target_changed {1}".format(PLACE_KEYBINDS[y][x], player))
        tf.eval("/edit -c0 gag_redef")

def trigger_party_message(message):
    stats = parse_message(message)
    bcproxy_stats[stats['player']] = stats

    update_places()
    update_status()

def trigger_target_changed(player):
    other_state['cast_target'] = player
    tf.eval("/set cast_target={0}".format(player))
    for member in bcproxy_stats:
        bcproxy_stats[member]['cast_target'] = member == player
    update_status()

def trigger_nergal_frontrow(opts):
    # WIP
    pss_stats = json.loads(opts)
    tf.out("nergal frontrow: opts {0}".format())

def pss_json_to_stats(j):
    return {
        'player': j.get('player'),
        'hp': j.get('hp'),
        'maxhp': j.get('maxhp'),
        'sp': j.get('sp'),
        'maxsp': j.get('maxsp'),
        'ep': j.get('ep'),
        'maxep': j.get('maxep'),
        'place_x': j.get('x'),
        'place_y': j.get('y'),
        'formation': j.get('state') == 'form',
        'member': j.get('state') == 'mbr',
        'entry': j.get('state') == 'ent',
        'following': j.get('state') == 'fol',
        'leader': j.get('state') == 'ldr',
        'linkdead': j.get('state') == 'ld',
        'resting': j.get('state') == 'rest',
        'idle': j.get('idle'),
        'invisible': j.get('player') == 'Someone',
        'dead': j.get('state') == 'dead',
        'stunned': j.get('state')[:3] == 'stu',
        'unconscious': j.get('stunned')[:3] == 'unc',
    }

for setup_command in SETUP_COMMANDS:
    tf.eval(setup_command)

tf.out("Loaded partystatus")
