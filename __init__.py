import csv
import math
import random
import thread
from ctypes import c_int
from multiprocessing import Value
import shelve
import textwrap

import libtcodpy as libtcod
from src import color, island_generator, loader, nonplayercharacter, playercharacter, tiles

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
BAR_WIDTH_TOP = SCREEN_WIDTH - 2
PANEL_HEIGHT = 7
PANEL_HEIGHT_TOP = 2
PANEL_BOTTOM = SCREEN_HEIGHT - PANEL_HEIGHT
PANEL_TOP = 0 + PANEL_HEIGHT_TOP
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50

LIMIT_FPS = 120  # 120 frames-per-second maximum (for testing)

FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
MAX_MONSTERS = 20

# GUI panel at the bottom/top of the screen
bottom_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
top_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT_TOP)
numKlicks = 0
time = 1

game_status = 1  # 0 = generator, 1 = game, 2 = menu, 3 = intro

game_msgs = []

shared_percent = Value(c_int)


class Info_text:
    def __init__(self, value):
        self.set(value)

    def get(self):
        return self.text

    def set(self, t):
        self.text = t


def is_blocked(x, y):
    if tile_list[map[x * MAP_SIZE + y]].move_blocked == 0:
        return True
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    return False


class Object:
    # A generic objecjt representing both the player and monsters, where entclass stands for entity class
    # and defines exactly whether it's a NPC or PC.
    def __init__(self, x, y, char, name, color, blocks=False, entclass=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name

        self.entclass = entclass
        if self.entclass:
            self.entclass.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

    def move(self, dx, dy):
        # move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self):
        # set the color and then draw the character that represents this object at its position
        (x, y) = relative_coordinates(self.x, self.y)
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, x, y,
                                 self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


# Transforms the in-map coordinates into those of the console itself
def relative_coordinates(x, y):
    (x, y) = (
        x - player.x + VISUAL_WIDTH / 2 + VISUAL_WIDTH_OFFSET, y - player.y + VISUAL_HEIGHT / 2 + VISUAL_HEIGHT_OFFSET)
    return (x, y)


class Player(Object):
    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, VISUAL_WIDTH / 2 + VISUAL_WIDTH_OFFSET, VISUAL_HEIGHT / 2 + VISUAL_HEIGHT_OFFSET,
                                 self.char, libtcod.BKGND_NONE)


def attackmove(dx, dy):
    # the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    # try to find an attackable object there
    target = None
    for object in objects:
        if object.entclass and object.x == x and object.y == y:
            target = object
            break

    # attack if target found, move otherwise
    if target is not None:
        player.entclass.attack(target)
    else:
        player.move(dx, dy)


def place_objects():
    while len(objects) <= MAX_MONSTERS:
        r = random.randrange(4)
        if r < 1:
            x = player.x + VISUAL_WIDTH + 5
            y = player.y + VISUAL_HEIGHT + random.randrange(-10, 10)

        elif 1 <= r < 2:
            x = player.x - VISUAL_WIDTH - 5
            y = player.y + VISUAL_HEIGHT + random.randrange(-10, 10)
        elif 2 <= r < 3:
            x = player.x + VISUAL_WIDTH + random.randrange(-10, 10)
            y = player.y + VISUAL_HEIGHT + 5

        elif 3 <= r < 4:
            x = player.x + VISUAL_WIDTH + random.randrange(-10, 10)
            y = player.y - VISUAL_HEIGHT - 5

        if not is_blocked(x, y):
            if random.randrange(100) < 60:  # 60% chance of getting an orc
                # create an orc
                monsterentity = nonplayercharacter.monster(hp=10, agility=4, strength=6, intelligence=3, level=1,
                                                           on_death=monster_death)
                ai = monsterAi()
                monster = Object(x, y, 'O', 'orc', libtcod.desaturated_green,
                                 blocks=True, entclass=monsterentity, ai=ai)
            else:
                # create a troll
                monsterentity = nonplayercharacter.monster(hp=15, agility=6, strength=5, intelligence=4, level=2,
                                                           on_death=monster_death)
                ai = monsterAi()
                monster = Object(x, y, 'T', 'troll', libtcod.darker_green,
                                 blocks=True, entclass=monsterentity, ai=ai)
            objects.append(monster)


class monsterAi():
    def take_turn(self):
        monster = self.owner
        if monster.distance_to(player) >= 2:
            monster.move_towards(player.x, player.y)
        elif player.entclass.hp > 0:
            monster.entclass.attack(player)


def update_visual_map():
    size = MAP_SIZE
    for x in range(VISUAL_WIDTH):
        for y in range(VISUAL_HEIGHT):
            map_x = x + player.x - VISUAL_WIDTH / 2
            map_y = y + player.y - VISUAL_HEIGHT / 2

            if map_x < size and map_y < size:
                visual[x][y] = map[map_x * size + map_y]


def make_visual_map():
    # fill map with "unblocked" tiles
    global visual
    visual = [[tiles.Tile(0, '?', 0, 0, "debug", "")
               for y in range(VISUAL_HEIGHT)]
              for x in range(VISUAL_WIDTH)]


def render_all():
    update_visual_map()

    global color_light_wall
    global color_light_ground

    # go through all tiles, and set their color
    for y in range(VISUAL_HEIGHT):
        for x in range(VISUAL_WIDTH):
            id = visual[x][y]

            # variation 1 - not good
            tile_color = tile_list[id].colors[0]
            if len(tile_list[id].colors) > 1:
                value = math.degrees((x + player.x - VISUAL_WIDTH / 2) + (y + player.y - VISUAL_HEIGHT / 2) * MAP_SIZE)
                print value
                if int(value) % 2 == 1:
                    tile_color = tile_list[id].colors[1]

            # animate if two colors
            if tile_list[id].animation_color != "":
                r = random.randrange(2)
                if r >= 1:
                    tile_color = tile_list[id].animation_color

            tile_variation = 0
            if 1 < len(tile_list[id].chars) <= 2:
                value = math.lgamma((x + player.x - VISUAL_WIDTH / 2)*MAP_SIZE + (y + player.y - VISUAL_HEIGHT / 2))
                print value
                if int(value) % 2 == 1:
                    tile_variation = 1

            elif len(tile_list[id].chars) > 2:
                value = math.lgamma((x + player.x - VISUAL_WIDTH / 2)*MAP_SIZE + (y + player.y - VISUAL_HEIGHT / 2))
                print value
                if int(value) % 3 == 1:
                    tile_variation = 1
                elif int(value) % 3 == 2:
                    tile_variation = 2


            libtcod.console_set_default_foreground(con, getattr(color, tile_color))
            libtcod.console_put_char(con, x + VISUAL_WIDTH_OFFSET, y + VISUAL_HEIGHT_OFFSET,
                                     int(tile_list[id].chars[tile_variation]),
                                     libtcod.BKGND_NONE)

    # draw all objects in the list
    place_objects()
    for object in objects:
        if object != player:
            object.draw()
        player.draw()

    print 'HP: ' + str(player.entclass.hp) + '/' + str(player.entclass.max_hp)

    # blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # prepare to render the GUI panel
    libtcod.console_set_default_background(top_panel, libtcod.black)
    libtcod.console_clear(top_panel)
    libtcod.console_set_default_background(bottom_panel, libtcod.black)
    libtcod.console_clear(bottom_panel)

    # print the game messages, one line at a time
    y = 1
    for (line, color_msg) in game_msgs:
        libtcod.console_set_default_foreground(bottom_panel, color_msg)
        libtcod.console_print_ex(bottom_panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # show the player's stats
    render_bar(bottom_panel, 1, 1, BAR_WIDTH, 'HP', player.entclass.hp, player.entclass.max_hp,
               libtcod.light_red, libtcod.darker_red)
    # shows the time
    render_timeLine(top_panel, 1, 1, BAR_WIDTH_TOP, 'O', calcTime(), 24, libtcod.dark_blue)
    # render_bar(top_panel, 1, 1, BAR_WIDTH_TOP, 'TIME', calcTime(), 24,
    #          libtcod.light_yellow, libtcod.dark_yellow)
    # display names of objects under the mouse
    libtcod.console_set_default_foreground(bottom_panel, libtcod.light_gray)
    libtcod.console_print_ex(bottom_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, '')

    # blit the contents of "panel" to the root console
    libtcod.console_blit(bottom_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_BOTTOM)
    libtcod.console_blit(top_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT_TOP, 0, 0, PANEL_TOP)


def message(new_msg, color_msg=libtcod.white):
    # split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        # add the new line as a tuple, with the text and the color
        game_msgs.append((line, color_msg))


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
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:  # (special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


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


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    # render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    # render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def calcTime():
    global time
    global numKlicks
    print numKlicks
    """if numKlicks < 12:
        time = 1
    elif 12 < numKlicks <= 24:
        time = 2
    elif 24 < numKlicks <= 36:
        time = 3
    elif 36 < numKlicks <= 48:
        time = 4
    elif 48 < numKlicks <= 60:
        time = 5
    elif 60 < numKlicks <= 72:
        time = 6
    elif 72 < numKlicks <= 84:
        time = 7
    elif 84 < numKlicks <= 96:
        time = 8
    elif 96 < numKlicks <= 108:
        time = 9
    elif 108 < numKlicks <= 120:
        time = 10
    elif 120 < numKlicks <= 132:
        time = 11
    elif 132 < numKlicks <= 144:
        time = 12
    elif 144 < numKlicks <= 156:
        time = 13
    elif 156 < numKlicks <= 168:
        time = 14
    elif 168 < numKlicks <= 180:
        time = 15
    elif 180 < numKlicks <= 192:
        time = 16
    elif 192 < numKlicks <= 204:
        time = 17
    elif 204 < numKlicks <= 216:
        time = 18
    elif 216 < numKlicks <= 228:
        time = 19
    elif 228 < numKlicks <= 240:
        time = 20
    elif 240 < numKlicks <= 252:
        time = 21
    elif 252 < numKlicks <= 264:
        time = 22
    elif 264 < numKlicks <= 276:
        time = 23
    elif 276 < numKlicks <= 288:
        time = 24
    elif numKlicks > 288:
        time = 0
        numKlicks = 0"""
    time = numKlicks
    if numKlicks > BAR_WIDTH_TOP:
        time = 1
        numKlicks = 0

    return time


def render_timeLine(panel, x, y, total_width, name, value, maximum, back_color):
    # render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    # render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # now render the bar on top
    libtcod.console_set_default_background(panel, libtcod.blue)
    x = value
    if bar_width > 0:
        libtcod.console_put_char_ex(panel, x, y, 15, libtcod.yellow, libtcod.blue)


def perk_menu(header, options1, options2):
    # show a menu with each item of the inventory as an option
    # if len(inventory) == 0:
    #   options = ['Inventory is empty.']
    # else:
    #    options = [item.name for item in inventory]
    options = []
    if options1:
        options = ['Opt 1', 'Opt 2', 'Opt 3']
    elif options2:
        options = ['Opt 1', 'Opt 2', 'Opt 3', 'Opt 4', 'Opt 5', 'Opt 6', 'Opt 7', 'Opt 8', 'Opt 9', 'Opt 10']

    index = menu(header, options, INVENTORY_WIDTH)

    # if an item was chosen, return it
    # if index is None or len(inventory) == 0: return None
    # return inventory[index].item
    return index


def msgbox(text, width=50):
    menu(text, [], width)  # use menu() as a sort of "message box"


def game_over(player):
    print 'You died!'
    player.char = '%'
    player.color = libtcod.dark_red


def save_game():
    # open a new empty shelve (possibly overwriting an old one) to write the game data
    '''
    file = shelve.open('player.sav', 'n')
    file['player_race']
    file['player_gender'] =  # index of player in objects list
    file['player_first_name']
    file['player_name']

    file['player_hp'] = player.entclass.hp
    file['player_agility'] = player.agility
    file['player_strength'] = player.strength
    file['player_intelligence']
    file['player_vitality']
    file['player_xp']
    file['player_level']
    file['player_max_hp']
    file['player_points']
    file['player_perks']

    file.close()
    '''


"""
def play_game():
    global key, mouse

    player_action = None

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():
        # render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        libtcod.console_flush()

        # erase all objects at their old locations, before they move
        for object in objects:
            object.clear()

        # handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        # let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
"""


def load_game():
    # open the previously saved shelve and load the game data
    global map, objects, player, inventory, game_msgs, game_state

    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  # get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    file.close()


"""
def new_game():
    global player, inventory, game_msgs, game_state

    # create object representing the player
    playerentity = playercharacter.entity(hp=100, strength=5, agility=5, intelligence=5, vitality=5, on_death=game_over)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', 'player', libtcod.white, blocks=True,
                    entclass=playerentity)

    # generate map (at this point it's not drawn to the screen)

    game_state = 'playing'
    inventory = []

    # create the list of game messages and their colors, starts empty
    game_msgs = []

    # welcoming message
    message('Welcome to Rogue Island stranger!', libtcod.red)
"""


def monster_death(monster):
    print monster.name.capitalize() + ' is dead!'
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.entclass = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name


def handle_keys():
    global numKlicks
    # key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  # turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True  # exit game

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        attackmove(0, -1)
        numKlicks += 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        attackmove(0, 1)
        numKlicks += 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        attackmove(-1, 0)
        numKlicks += 1
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        attackmove(1, 0)
        numKlicks += 1
    else:
        # return 'player_pass'
        key_char = chr(key.c)

        if key_char == 'p' and not libtcod.console_is_key_pressed(key):
            # show in-game menu
            chosen_option = perk_menu('Press the key next to the perk you want to use.\n', 1, 0)
            if chosen_option is 0:
                chosen_perk = perk_menu('Perk Menu with 10 Options.\n', 0, 1)

            elif chosen_option is 1:
                chosen_perk = perk_menu('Perk Menu with 10 Options.\n', 0, 1)

            elif chosen_option is 2:
                chosen_perk = perk_menu('Perk Menu with 10 Options.\n', 0, 1)


def load_tiles():
    with open("data/configurations/tiles.csv", 'rb') as f:
        mycsv = csv.reader(f, delimiter=';')
        mycsv = list(mycsv)

    for value in range(len(mycsv) - 1):
        name = mycsv[value + 1][1]
        chars = mycsv[value + 1][2]
        move_blocked = int(mycsv[value + 1][6])
        sight_block = int(mycsv[value + 1][7])
        color = mycsv[value + 1][8]
        animation_color = mycsv[value + 1][9]

        tile = tiles.Tile(name, chars, move_blocked, sight_block, color, animation_color)
        tile_list.append(tile)


def update_info(text):
    middle = SCREEN_WIDTH / 2 - len(text) / 2
    text = str(((float(shared_percent.value) / MAP_SIZE ** 2) * 100) + 6.5) + "%%"
    libtcod.console_print(0, middle, SCREEN_HEIGHT / 2, text)


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('data/fonts/terminal' + str(FONT_SIZE) + 'x' + str(FONT_SIZE) + '_gs_ro.png',
                                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'ASCII Adventure', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
global map
global tile_list
tile_list = []

if game_status == 0:
    info_text = Info_text("                                                                              ")
    generator_thread = thread.start_new_thread(island_generator.start, (MAP_SIZE, shared_percent))

if game_status == 1:
    load_tiles()
    map = loader.load_map()

    # create the entity and the object of the player
    playerentity = playercharacter.entity(hp=100, strength=5, agility=5, intelligence=5, vitality=5, on_death=game_over)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', 'player', libtcod.white, blocks=True,
                    entclass=playerentity)
    objects = []
    objects.append(player)

    player.x = 100
    player.y = 100

    make_visual_map()

    player_action = None

while not libtcod.console_is_window_closed():

    if game_status == 0:
        update_info(info_text.get())
        # print generator_thread

    libtcod.console_flush()

    if game_status == 1:
        # render the screen
        render_all()
        # erase all objects at their old locations, before they move
        for object in objects:
            object.clear()

        ###########################
        # DRAW INTERFACE HERE
        ###########################

        # handle keys and exit game if needed
        exit = handle_keys()

        if game_status == 1 and player_action != 'player_pass':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
    # Intro
    if game_status == 3:
        img = libtcod.image_load("data/images/intro_2.png")
        libtcod.image_blit_rect(img, 0, 0, 0, -1, -1, libtcod.BKGND_SET)
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)
