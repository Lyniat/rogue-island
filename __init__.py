import csv
import random
import math
import thread
from ctypes import c_int
from multiprocessing import Value

import color
import island_generator
import libtcodpy as libtcod
import loader
import nonplayercharacter
import playercharacter
import tiles

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

LIMIT_FPS = 120  # 120 frames-per-second maximum (for testing)

FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
MAX_MONSTERS = 20;

game_status = 1  # 0 = generator, 1 = game, 2 = menu

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

            tile_color = tile_list[id].color
            # animate if two colors
            if tile_list[id].animation_color != "":
                r = random.randrange(2)
                if r >= 1:
                    tile_color = tile_list[id].animation_color

            libtcod.console_set_default_foreground(con, getattr(color, tile_color))
            libtcod.console_put_char(con, x + VISUAL_WIDTH_OFFSET, y + VISUAL_HEIGHT_OFFSET, tile_list[id].char,
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


def game_over(player):
    print 'You died!'
    player.char = '%'
    player.color = libtcod.dark_red


def monster_death(monster):
    print monster.name.capitalize() + ' is dead!'
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.entclass = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name


def handle_keys():
    # key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  # turn-based

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True  # exit game

    # movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        attackmove(0, -1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        attackmove(0, 1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        attackmove(-1, 0)

    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        attackmove(1, 0)

    else:
        return 'player_pass'


def load_tiles():
    with open("data/configurations/tiles.csv", 'rb') as f:
        mycsv = csv.reader(f, delimiter=';')
        mycsv = list(mycsv)

    for value in range(len(mycsv) - 1):
        name = mycsv[value + 1][1]
        char = mycsv[value + 1][2]
        move_blocked = int(mycsv[value + 1][6])
        sight_block = int(mycsv[value + 1][7])
        color = mycsv[value + 1][8]
        animation_color = mycsv[value + 1][9]

        tile = tiles.Tile(name, char, move_blocked, sight_block, color, animation_color)
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
