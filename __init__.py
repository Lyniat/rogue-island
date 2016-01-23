import csv
import math
import random
import textwrap
import thread
from ctypes import c_int
from multiprocessing import Value

import libtcodpy as libtcod
from src import color, island_generator, loader, nonplayercharacter, playercharacter, tiles, gui, globalvars

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

LIMIT_FPS = 30  # 30 frames-per-second

FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
MAX_MONSTERS = 20

# GUI panel at the bottom/top of the screen
bottom_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
top_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT_TOP)
numClicks = 0
time = 1

game_status = 1  # 0 = generator, 1 = game, 2 = menu, 3 = intro

game_msgs = []

shared_percent = Value(c_int)

objects = []

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

    def move_towards(self, object):
        dx = object.x - self.x
        dy = object.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


"""
    def move_astar(self, target):
        # This creates a 'minimap' of the visible screen
        fov = libtcod.map_new(VISUAL_WIDTH, VISUAL_HEIGHT)
        # Get the position of the top left tile for further calculations
        start_tile_x = player.x - 27
        start_tile_y = player.y - 37
        # Scan the current map for blocking walls and objects
        for y1 in range(VISUAL_HEIGHT):
            for x1 in range(VISUAL_WIDTH):
                if is_blocked(start_tile_x + x1, start_tile_y + y1):
                    libtcod.map_set_properties(fov, start_tile_x + x1, start_tile_y + y1, True, False)

        for obj in objects:
            if obj.blocks and obj != self and obj != target:
                # Set the tile as a wall so it must be navigated around
                (x, y) = relative_coordinates(obj.x, obj.y)
                libtcod.map_set_properties(fov, x, y, True, False)

        # Allocate a A* path using the libtcod provided library
        my_path = libtcod.path_new_using_map(fov, 0)

        # Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            print 'hm'
            self.move_towards(target.x, target.y)
"""


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

    # attack if target found, move otherwise - first proximity block is checked in case perk Dungeon Basher is taken

    if target is not None:

        if is_blocked(target.x - 1, target.y):
            globalvars.monster_proximity_block[3] = 1
        if is_blocked(target.x + 1, target.y):
            globalvars.monster_proximity_block[1] = 1
        if is_blocked(target.x, target.y - 1):
            globalvars.monster_proximity_block[0] = 1
        if is_blocked(target.x, target.y + 1):
            globalvars.monster_proximity_block[2] = 1

        print globalvars.monster_proximity_block

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
        if monster.entclass.stunned == 0:
            if monster.distance_to(player) >= 2:
                monster.move_towards(player)
            elif player.entclass.hp > 0:
                monster.entclass.attack(player)
        elif monster.entclass.stunned == 1:
            print '*UNSTUNNED*'
            monster.entclass.stunned = 0


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
                if int(value) % 2 == 1:
                    tile_color = tile_list[id].colors[1]

            # animate if two colors
            if tile_list[id].animation_color != "":
                r = random.randrange(2)
                if r >= 1:
                    tile_color = tile_list[id].animation_color

            tile_variation = 0
            if 1 < len(tile_list[id].chars) <= 2:
                value = math.lgamma((x + player.x - VISUAL_WIDTH / 2) * MAP_SIZE + (y + player.y - VISUAL_HEIGHT / 2))
                if int(value) % 2 == 1:
                    tile_variation = 1

            elif len(tile_list[id].chars) > 2:
                value = math.lgamma((x + player.x - VISUAL_WIDTH / 2) * MAP_SIZE + (y + player.y - VISUAL_HEIGHT / 2))
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
    gui.render_hp_bar(bottom_panel, 1, 1, BAR_WIDTH, 'HP', player.entclass.hp, player.entclass.max_hp,
                      libtcod.light_red, libtcod.darker_red)
    # shows the time
    gui.render_timeLine(top_panel, 0, 0, BAR_WIDTH_TOP, calc_time(), color.blue)
    # render_bar(top_panel, 1, 1, BAR_WIDTH_TOP, 'TIME', calcTime(), 24,
    #          libtcod.light_yellow, libtcod.dark_yellow)
    # display names of objects under the mouse
    libtcod.console_set_default_foreground(bottom_panel, libtcod.light_gray)
    libtcod.console_print_ex(bottom_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, '')

    # blit the contents of "panel" to the root console
    libtcod.console_blit(bottom_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_BOTTOM)
    libtcod.console_blit(top_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT_TOP, 0, 0, PANEL_TOP)


def calc_time():
    global time
    global numClicks

    if numClicks % 2 == 0:
        time += 1
    # time = numKlicks
    if time > BAR_WIDTH_TOP - 1:
        time = 0
        numClicks = 0

    return time


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


def game_over(player):
    message('You died!')
    player.char = '%'
    player.color = libtcod.dark_red


def monster_death(monster):
    message(str(monster.name) + ' is dead!')
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.entclass = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name


def handle_keys():
    global numClicks
    # key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  # turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True  # exit game

    if game_status == 1:
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            attackmove(0, -1)
            globalvars.player_y = player.y
            numClicks += 1
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            attackmove(0, 1)
            globalvars.player_y = player.y
            numClicks += 1
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            attackmove(-1, 0)
            globalvars.player_x = player.x
            numClicks += 1
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            attackmove(1, 0)
            globalvars.player_x = player.x
            numClicks += 1
        else:
            # return 'player_pass'
            key_char = chr(key.c)

            if key_char == 'p' and not libtcod.console_is_key_pressed(key):
                # show in-game menu
                chosen_option = gui.perk_menu('Press the key next to the perk you want to use.\n', 1, 0)
                if chosen_option is 0:
                    chosen_perk = gui.perk_menu('Perk Menu with 10 Options.\n', 0, 1)

                elif chosen_option is 1:
                    chosen_perk = gui.perk_menu('Perk Menu with 10 Options.\n', 0, 1)

                elif chosen_option is 2:
                    chosen_perk = gui.perk_menu('Perk Menu with 10 Options.\n', 0, 1)

            if key_char == 'i' and not libtcod.console_is_key_pressed(key):
                # show black screen in game
                gui.text_menu()

            if key_char == 'x' and not libtcod.console_is_key_pressed(key):
                gui.save_game(player, objects)
                message('Game saved!')


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


# returns selected option
def main_menu():
    img = libtcod.image_load('menu_background.png')
    global game_status
    while not libtcod.console_is_window_closed():
        # show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        # show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                 'ROGUE ISLAND')
        libtcod.console_print_ex(0, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                                 '')

        # show options and wait for the player's choice
        choice = gui.menu('', ['Generate Map', 'Play a new game', 'Continue last game', 'Quit'], 24)
        if choice == 0:
            # generate map
            game_status = 0
            return game_status

        if choice == 1:  # new game
            game_status = 1

            player.x = 100
            player.y = 100

            return game_status
        if choice == 2:  # load last game
            try:
                gui.load_game(player, map, objects)
                print objects
            except:
                gui.msgbox('\n No saved game to load.\n', 24)
                continue
            game_status = 1

            return game_status
        elif choice == 3:  # quit
            return


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('data/fonts/terminal' + str(FONT_SIZE) + 'x' + str(FONT_SIZE) + '_gs_ro.png',
                                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'ASCII Adventure', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

# create the entity and the object of the player
playerentity = playercharacter.entity(hp=100, strength=5, agility=5, intelligence=5, vitality=5,
                                      first_name='Lennard', name='Cooper', race='human', gender='f',
                                      on_death=game_over)
player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', 'player', libtcod.white, blocks=True,
                entclass=playerentity)

game_status = main_menu()
global map
global tile_list
tile_list = []

if game_status == 0:
    info_text = Info_text("                                                                              ")
    generator_thread = thread.start_new_thread(island_generator.start, (MAP_SIZE, shared_percent))

if game_status == 1:
    load_tiles()
    map = loader.load_map()

    objects.append(player)

    globalvars.player_x = player.x
    globalvars.player_y = player.y

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
        print 'pass'
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
