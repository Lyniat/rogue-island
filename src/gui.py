import shelve
import textwrap
from ctypes import c_int
from multiprocessing import Value

import libtcodpy as libtcod
from src import color

# actual size of the window
SCREEN_WIDTH = 90
SCREEN_HEIGHT = 65

FONT_SIZE = 12  # 8 = small, 12 = normal, 16 = big

# size of the map
MAP_SIZE = 512

VISUAL_WIDTH = 75
VISUAL_HEIGHT = 55
VISUAL_WIDTH_OFFSET = 0
VISUAL_HEIGHT_OFFSET = 1

# sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
BAR_WIDTH_TOP = VISUAL_WIDTH
PANEL_HEIGHT = 7
PANEL_HEIGHT_TOP = 1
PANEL_BOTTOM = SCREEN_HEIGHT - PANEL_HEIGHT
PANEL_TOP = 0
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50

PANEL_SIDE_WIDTH = SCREEN_WIDTH - VISUAL_WIDTH
PANEL_SIDE_HEIGHT = SCREEN_HEIGHT
PANEL_SIDE_X_POS = VISUAL_WIDTH
PANEL_SIDE_Y_POS = 0

LIMIT_FPS = 120  # 120 frames-per-second maximum (for testing)
TORCH_RADIUS = 10
MAX_MONSTERS = 20

# GUI panel at the bottom/top of the screen
bottom_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
top_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT_TOP)
side_panel = libtcod.console_new(PANEL_SIDE_WIDTH, PANEL_SIDE_HEIGHT)
numKlicks = 0
time = 0
# graphical elements relevant for HP and XP bar
ascii_block = 176
ascii_sun = 15
i = 1

# variables relevant for bar representation
max_range_hp = 19
max_range_xp = 0
hp_step_count = 1
xp_step_count = 1

game_status = 1  # 0 = generator, 1 = game, 2 = menu

shared_percent = Value(c_int)

game_msgs = []
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)


def render_exp_bar(panel, x, y, total_width, name, value, maximum):
    global ascii_block
    global xp_step_count
    global max_range_xp
    default_x = x

    steps = maximum / 20

    if value > xp_step_count * steps:
        max_range_xp = xp_step_count * steps
        xp_step_count += 1

    if xp_step_count >= maximum:
        xp_step_count = 0
    for num in range(max_range_xp):
        libtcod.console_put_char_ex(panel, x, y, ascii_block, color.yellow, color.black)
        x += 1

    libtcod.console_set_default_foreground(panel, color.white)
    libtcod.console_print_ex(panel, default_x + total_width / 2, y + 1, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def render_hp_bar(panel, x, y, total_width, name, value, maximum):
    global ascii_block
    global hp_step_count
    global max_range_hp
    default_x = x
    steps = maximum / 19

    if value < (maximum - hp_step_count * steps):
        max_range_hp -= 1
        hp_step_count += 1

    if value > 0:
        for num in range(max_range_hp):
            libtcod.console_put_char_ex(panel, x, y, ascii_block, color.red, color.black)
            x += 1

    libtcod.console_set_default_foreground(panel, color.white)
    libtcod.console_print_ex(panel, default_x + total_width / 2, y + 1, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def render_timeLine(panel, x, y, total_width, value, back_color):
    global ascii_sun
    global VISUAL_WIDTH
    # render a bar (HP, experience, etc). first calculate the width of the bar
    # bar_width = int(float(value) / maximum * total_width)
    bar_width = VISUAL_WIDTH
    # render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # now render the bar on top
    libtcod.console_set_default_background(panel, color.blue)
    x = value
    if bar_width > 0:
        libtcod.console_put_char_ex(panel, x, y, ascii_sun, color.yellow, color.blue)


"""
def get_names_under_mouse():
    global mouse

    # return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y]

    names = ', '.join(names)  # join the names, separated by commas
    return names.capitalize()
"""


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)
    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:  # (special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


# renders the charge menu
def charge_menu():
    options = ['Charge', 'Hurl', 'Word of Power', 'Arcane Missiles', 'Fireball', 'Frozen Tomb', 'Enormous Blast',
               'Weapon Throw', 'Flurry']
    index = menu('Charges', options, INVENTORY_WIDTH)
    return index


def perk_menu(header, options1, chosen_option):
    options = []
    if options1:
        options = ['Fortitude - Strengthens your durability', 'Cunning - Provides Utility based on Intelligence',
                   'Savagery - Improves your damage']

    if chosen_option is 0:
        options = ['Iron Will', 'Veteran\'s Scars', 'Ignore The Pain', 'Ram', 'Stunning', 'Dungeon Basher', 'Charge',
                   'Deflect', 'Hurl']
    elif chosen_option is 1:
        options = ['Paladin', 'Warmth', 'Word of Power', 'Arcane Missiles', 'Fireball', 'Frozen Tomb', 'Rogue',
                   'Vampirism', 'Soulreaver']
    elif chosen_option is 2:
        options = ['Soldier', 'Combattant', 'Warmonger', 'Second Strike', 'Multistrike', 'Enormous Blast',
                   'First Strike', 'Weapon Throw', 'Flurry']

    index = menu(header, options, INVENTORY_WIDTH)

    return index


def render_border(interface, interfaceWidth, interfaceHeight):
    HORIZONTAL_BORDER = 205
    VERTICAL_BORDER = 186

    for j in range(interfaceHeight + 1):
        for i in range(interfaceWidth + 1):
            if j == 0 or j == VISUAL_HEIGHT - 1:
                libtcod.console_put_char_ex(interface, i, j, HORIZONTAL_BORDER, libtcod.white, libtcod.black)
            elif i == 0 or i == VISUAL_WIDTH - 1:
                libtcod.console_put_char_ex(interface, i, j, VERTICAL_BORDER, libtcod.white, libtcod.black)


def text_menu():
    # generisch machen: in range anstatt visual... die interface groesse schreiben
    text_window = libtcod.console_new(VISUAL_WIDTH, VISUAL_HEIGHT)

    render_border(text_window, VISUAL_WIDTH, VISUAL_HEIGHT)

    libtcod.console_print(text_window, VISUAL_WIDTH / 4, VISUAL_HEIGHT / 2, 'Hier koennte Ihr String stehen')

    libtcod.console_blit(text_window, 0, 0, VISUAL_WIDTH, VISUAL_HEIGHT, 0, 0, 1, 1.0, 1.0)
    libtcod.console_flush()


def message(new_msg, color_msg=libtcod.white):
    # split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        # add the new line as a tuple, with the text and the color
        game_msgs.append((line, color_msg))


def msgbox(text, width=50):
    menu(text, [], width)  # use menu() as a sort of "message box"


def save_game(player, objects):
    # open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('player.sav', 'n')
    file['player_race'] = player.entclass.race
    file['player_gender'] = player.entclass.gender
    file['player_first_name'] = player.entclass.first_name
    file['player_name'] = player.entclass.name

    file['player_pos_x'] = player.x
    file['player_pos_y'] = player.y

    file['player_hp'] = player.entclass.hp
    file['player_agility'] = player.entclass.agility
    file['player_strength'] = player.entclass.strength
    file['player_intelligence'] = player.entclass.intelligence
    file['player_vitality'] = player.entclass.vitality
    file['player_xp'] = player.entclass.xp
    file['player_level'] = player.entclass.level
    file['player_max_hp'] = player.entclass.max_hp
    file['player_'] = player.entclass.points
    file['player_perks'] = player.entclass.perks

    file.close()

    file = shelve.open('objects.sav', 'n')
    file['objects'] = objects
    file.close()


def load_game(player, map, objects):
    # open the previously saved shelve and load the game data
    file = shelve.open('player.sav', 'r')
    player.entclass.race = file['player_race']
    player.entclass.gender = file['player_gender']
    player.entclass.first_name = file['player_first_name']
    player.entclass.name = file['player_name']

    player.x = file['player_pos_x']
    player.y = file['player_pos_y']

    player.entclass.hp = file['player_hp']
    file.close()

    file = shelve.open('objects.sav', 'r')
    objects = file['objects']
    file.close()

    print("loaded")


def perk_charge(panel, healthpots, idx0, idx1, idx2, idx3, idx4, idx5, idx6, idx7, idx8):
    charges = ['Health Pots: ' + str(healthpots), 'Charge' + str(idx0), 'Hurl' + str(idx0), 'Word of Power' + str(idx0),
               'Arcane Missiles' + str(idx0), 'Fireball' + str(idx0), 'Frozen Tomb' + str(idx0),
               'Enormous Blast' + str(idx0),
               'Weapon Throw' + str(idx0), 'Flurry' + str(idx0)]
    if healthpots is not -1:
        libtcod.console_set_default_foreground(panel, color.red)
        libtcod.console_print_ex(panel, 0, 2, libtcod.BKGND_NONE, libtcod.LEFT, charges[0])
    if idx0 is not -1:
        libtcod.console_set_default_foreground(panel, color.gray)
        libtcod.console_print_ex(panel, 0, 5, libtcod.BKGND_NONE, libtcod.LEFT, charges[1])
    if idx1 is not -1:
        libtcod.console_set_default_foreground(panel, color.aqua)
        libtcod.console_print_ex(panel, 0, 8, libtcod.BKGND_NONE, libtcod.LEFT, charges[2])
    if idx2 is not -1:
        libtcod.console_set_default_foreground(panel, color.fuchsia)
        libtcod.console_print_ex(panel, 0, 11, libtcod.BKGND_NONE, libtcod.LEFT, charges[3])
    if idx3 is not -1:
        libtcod.console_set_default_foreground(panel, color.red)
        libtcod.console_print_ex(panel, 0, 14, libtcod.BKGND_NONE, libtcod.LEFT, charges[4])
    if idx4 is not -1:
        libtcod.console_set_default_foreground(panel, color.blue)
        libtcod.console_print_ex(panel, 0, 17, libtcod.BKGND_NONE, libtcod.LEFT, charges[5])
    if idx5 is not -1:
        libtcod.console_set_default_foreground(panel, color.green)
        libtcod.console_print_ex(panel, 0, 20, libtcod.BKGND_NONE, libtcod.LEFT, charges[6])
    if idx6 is not -1:
        libtcod.console_set_default_foreground(panel, color.maroon)
        libtcod.console_print_ex(panel, 0, 23, libtcod.BKGND_NONE, libtcod.LEFT, charges[7])
    if idx7 is not -1:
        libtcod.console_set_default_foreground(panel, color.teal)
        libtcod.console_print_ex(panel, 0, 26, libtcod.BKGND_NONE, libtcod.LEFT, charges[8])
    if idx8 is not -1:
        libtcod.console_set_default_foreground(panel, color.teal)
        libtcod.console_print_ex(panel, 0, 29, libtcod.BKGND_NONE, libtcod.LEFT, charges[9])
