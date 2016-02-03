import csv
import math
import random
import sys
import textwrap
import thread
from ctypes import c_int
from multiprocessing import Value

import libtcodpy as libtcod
from src import color, island_generator, loader, playercharacter, tiles, gui, globalvars, \
    object, world

#############################################
#
# Dieses Spiel basiert teilweise auf dem Python-libtcod-Tutorial von Roguebasin
# http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod
#
#############################################

# actual size of the window
SCREEN_WIDTH = 90
SCREEN_HEIGHT = 65

FONT_SIZE = 8  # 8 = small, 12 = normal, 16 = big

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
SIDE_PANEL_WIDTH = SCREEN_WIDTH - VISUAL_WIDTH
SIDE_PANEL_HEIGHT = SCREEN_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50

LIMIT_FPS = 30  # 30 frames-per-second

FOV_ALGO = 1  # default FOV algorithm
FOV_LIGHT_WALLS = True
torch_radius = 10
MAX_MONSTERS = 20

# GUI panel at the bottom/top of the screen
bottom_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
top_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT_TOP)
side_panel = libtcod.console_new(SIDE_PANEL_WIDTH, SIDE_PANEL_HEIGHT)
numClicks = 0
time = 1
mouse = libtcod.Mouse()
key = libtcod.Key()
player_action = 'not passed'
game_status = 2  # 0 = generator, 1 = game, 2 = menu, 3 = intro
fov_recompute = True

shared_percent = Value(c_int)

objects = []


class Info_text:
    def __init__(self, value):
        self.set(value)

    def get(self):
        return self.text

    def set(self, t):
        self.text = t


""" WIP: A* algorithm - at the moment helluva slow thing
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
            self.move_towards(target.x, target.y)
"""


# Transforms the in-map coordinates into those of the console itself
def relative_coordinates(x, y):
    (x, y) = (
        x - player.x + VISUAL_WIDTH / 2 + VISUAL_WIDTH_OFFSET, y - player.y + VISUAL_HEIGHT / 2 + VISUAL_HEIGHT_OFFSET)
    return (x, y)


class Player(object.Object):
    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, VISUAL_WIDTH / 2 + VISUAL_WIDTH_OFFSET, VISUAL_HEIGHT / 2 + VISUAL_HEIGHT_OFFSET,
                                 self.char, libtcod.BKGND_NONE)


def attackmove(dx, dy):
    # sun status
    global numClicks
    numClicks += 1

    # the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    # try to find an attackable object there
    target = None
    for object in world.objects:
        if object.entclass and object.x == x and object.y == y:
            target = object
            break

    # attack if target found, move otherwise - first proximity block is checked in case perk Dungeon Basher is taken

    if target is not None:
        if player.entclass.perks[2][1] == 1:
            if tile_list[map[(target.x - 1) * MAP_SIZE + target.y]].move_blocked:
                globalvars.monster_proximity_block[3] = 1
            if tile_list[map[(target.x + 1) * MAP_SIZE + target.y]].move_blocked:
                globalvars.monster_proximity_block[1] = 1
            if tile_list[map[(target.x) * MAP_SIZE + target.y - 1]].move_blocked:
                globalvars.monster_proximity_block[0] = 1
            if tile_list[map[(target.x) * MAP_SIZE + target.y + 1]].move_blocked:
                globalvars.monster_proximity_block[2] = 1

        player.entclass.attack(target)
    else:
        player.move(dx, dy)


def cast_spells(spell_id):
    if spell_id == 0:  # charge
        if player.entclass.perks[0][2] == 1:
            message('Left-click an enemy to charge it.', libtcod.light_cyan)
            monster = target_monster()
            if monster is not None:
                while player.distance_to_object(monster) > 1:
                    player.move_towards_object(monster)
                player.entclass.attack(monster)
            else:
                message('You did not charge.', libtcod.white)

            render_all()
        else:
            message('Your feet won\'t carry you fast enough.')

    if spell_id == 1:  # hurl
        if player.entclass.perks[2][2] == 1:
            message('Left-click an enemy to hurl it around.', libtcod.light_cyan)
            monster = target_monster(max_range=1)
            if monster is not None:
                monster.x += random.randint(-3, 3)
                monster.y += random.randint(-3, 3)
                monster.entclass.take_damage(player.entclass.vitality * 10)
                message(
                    'You hurl your enemy around, dealing massive ' + str(player.entclass.vitality * 10) + ' damage!')
            else:
                message('You did not hurl anything.', libtcod.white)
        else:
            message('You lack the necessary strength to hurl your enemy.')
    if spell_id == 2:  # word of power
        if player.entclass.perks[2][3] == 1:
            for obj in world.objects:  # damage every monster in range
                if obj is not player and obj.distance_to_object(player) <= 10:
                    message('The ' + obj.name + ' gets struck by the wave of energy and suffers ' + str(
                        player.entclass.intelligence + player.entclass.vitality + player.entclass.strength) + ' damage.',
                            color.fuchsia)
                    obj.entclass.take_damage(
                        player.entclass.vitality + player.entclass.intelligence + player.entclass.strength)
            render_all()
        else:
            message('You have no idea of Words of Power.')
    if spell_id == 3:  # arcane missiles
        if player.entclass.perks[0][4] == 1:
            monster = closest_monster(10)
            if monster is None:  # no enemy found within maximum range
                message('No enemy is close enough to aim at.', color.red)
                return 'cancelled'

            message(
                'You hit ' + monster.name + ' three times with your arcane missile. ' + monster.name + ' takes ' + str(
                    player.entclass.intelligence) + ' damage.', color.aqua)
            monster.entclass.take_damage(player.entclass.intelligence)
            render_all()
        else:
            message('You have not learned the arts of arcane missiles.')
    if spell_id == 4:  # fireball
        if player.entclass.perks[1][4] == 1:
            message('Left-click a target tile for the fireball, or right-click to cancel.', color.white)
            (x, y) = target_tile()
            if x is None: return 'cancelled'
            message('The fireball explodes, burning everything in a fiery inferno!', color.maroon)

            for obj in world.objects:  # damage every fighter in range, excluding the player
                (object_x, object_y) = relative_coordinates(obj.x, obj.y)
                if obj is not player and obj.entclass is not None and -5 <= (object_x - x) <= 5 and -5 <= (
                            object_y - y) <= 5:
                    message(
                        'The ' + obj.name + ' gets burned for ' + str(player.entclass.intelligence) + ' hit points.',
                        color.maroon)
                    obj.entclass.take_damage(player.entclass.intelligence)
                elif obj is player:
                    player.entclass.hp += player.entclass.intelligence
            render_all()
        else:
            message('You move your hands around, but nothing happens. No fireball for you!')

    if spell_id == 5:  # Frozen Tomb
        if player.entclass.perks[2][4] == 1:
            message('Left-click an enemy to freeze it to death.', color.blue)
            monster = target_monster()
            if monster is not None:
                monster.entclass.frozentomb = 1
            else:
                message('You did not use your power.', color.white)
            render_all()
        else:
            message('You try to concentrate, but you fail miserably.')
    if spell_id == 6:  # Enormous Blast
        if player.entclass.perks[2][7] == 1:
            message('An earthquake shatters the ground, heavily damaging everyone around you.')
            for obj in world.objects:
                if obj is not player and obj.entclass is not None:
                    if obj.distance_to_object(player) == 3:
                        obj.entclass.take_damage(1 * (player.entclass.agility + player.entclass.strength))
                        message('The earthquake barely reaches ' + str(obj.name) +
                                ' and damages it for ' + str(1 * (player.entclass.agility + player.entclass.strength)))
                    if obj.distance_to_object(player) == 2:
                        obj.entclass.take_damage(2 * (player.entclass.agility + player.entclass.strength))
                        message('The earthquake reaches ' + str(obj.name) +
                                ' and damages it for ' + str(2 * (player.entclass.agility + player.entclass.strength)))
                    if obj.distance_to_object(player) == 1:
                        obj.entclass.take_damage(4 * (player.entclass.agility + player.entclass.strength))
                        message('The earthquake devastates ' + str(obj.name) +
                                ' and damages it for ' + str(4 * (player.entclass.agility + player.entclass.strength)))
            render_all()
        else:
            message('You smash your hand into the ground, but absolutely nothing happens.')
    if spell_id == 7:  # Weapon Throw
        if player.entclass.perks[1][8] == 1:
            message('Left-click an enemy to throw your weapon at it.', color.white)
            monster = target_monster()
            if monster is not None:
                player.entclass.attack(monster)
                message('You concentrate and find your weapon in your hand again. And you are not even a wizard!')
            else:
                message('You could not bear losing your beloved weapon.', color.white)

            render_all()
        else:
            message('The fear to lose your weapon absolutely scares you.')


def target_monster(max_range=None):
    while True:
        (x, y) = target_tile(max_range)
        if x is None:
            return None

        for obj in world.objects:
            (object_x, object_y) = relative_coordinates(obj.x, obj.y)
            if object_x == x and object_y == y and obj != player:
                return obj


def target_tile(max_range=None):
    global key, mouse
    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()

        (x, y) = (mouse.cx, mouse.cy)
        if mouse.lbutton_pressed:
            return (x, y)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  # cancel if the player right-clicked or pressed Escape


def game_over(player):
    sys.exit()


def monster_death(monster):
    message(str.capitalize(monster.name) + ' is dead!')
    # Vampirism Perk
    if player.entclass.perks[1][5] == 1:
        player.entclass.hp += int(monster.entclass.hp / 2)
    # Soul Reaver Stack Gain
    if player.entclass.perks[2][5] == 1:
        player.entclass.souls += 1
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.entclass = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name

    if random.randint(0, 100) <= 20:
        player.entclass.pots += 1
        message('You found a health pot. (U to use it)')


def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1

    for object in world.objects:
        if object.entclass and not object == player:
            # calculate distance between this object and the player
            dist = player.distance_to_object(object)
            if dist < closest_dist:
                closest_enemy = object
                closest_dist = dist
    return closest_enemy


def update_visual_map():
    size = MAP_SIZE
    for x in range(VISUAL_WIDTH):
        for y in range(VISUAL_HEIGHT):
            map_x = x + player.x - VISUAL_WIDTH / 2
            map_y = y + player.y - VISUAL_HEIGHT / 2

            if map_x < size and map_y < size:
                visual[x][y] = world.map[map_x * size + map_y]


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
    global fov_recompute
    if fov_recompute:
        # recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, torch_radius, FOV_LIGHT_WALLS, FOV_ALGO)
        libtcod.console_clear(con)
        # go through all tiles, and set their color
        for y in range(VISUAL_HEIGHT):
            for x in range(VISUAL_WIDTH):
                (map_x, map_y) = (player.x + x - VISUAL_WIDTH / 2, player.y + y - VISUAL_HEIGHT / 2)
                visible = libtcod.map_is_in_fov(fov_map, map_x, map_y)
                # wall = map[x][y].block_sight
                id = visual[x][y]
                if not visible:
                    # it's out of the player's FOV
                    libtcod.console_set_char_background(con, x + VISUAL_WIDTH_OFFSET, y + VISUAL_HEIGHT_OFFSET,
                                                        color.black, libtcod.BKGND_SET)
                else:
                    tile_color = tile_list[id].colors[0]
                    if len(tile_list[id].colors) > 1:
                        value = math.degrees(
                            (x + player.x - VISUAL_WIDTH / 2) + (y + player.y - VISUAL_HEIGHT / 2) * MAP_SIZE)
                        if int(value) % 2 == 1:
                            tile_color = tile_list[id].colors[1]

                    # animate if two colors
                    if tile_list[id].animation_color != "":
                        r = random.randrange(2)
                        if r >= 1:
                            tile_color = tile_list[id].animation_color

                    tile_variation = 0
                    if 1 < len(tile_list[id].chars) <= 2:
                        value = math.lgamma(
                            (x + player.x - VISUAL_WIDTH / 2) * MAP_SIZE + (y + player.y - VISUAL_HEIGHT / 2))
                        if int(value) % 2 == 1:
                            tile_variation = 1

                    elif len(tile_list[id].chars) > 2:
                        value = math.lgamma(
                            (x + player.x - VISUAL_WIDTH / 2) * MAP_SIZE + (y + player.y - VISUAL_HEIGHT / 2))
                        if int(value) % 3 == 1:
                            tile_variation = 1
                        elif int(value) % 3 == 2:
                            tile_variation = 2

                    libtcod.console_set_default_foreground(con, getattr(color, tile_color))
                    libtcod.console_put_char(con, x + VISUAL_WIDTH_OFFSET, y + VISUAL_HEIGHT_OFFSET,
                                             int(tile_list[id].chars[tile_variation]),
                                             libtcod.BKGND_NONE)

    for object in world.objects:
        if object != player:
            if libtcod.map_is_in_fov(fov_map, object.x, object.y):
                object.draw()
        player.draw()

    # blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    # prepare to render the GUI panel
    libtcod.console_set_default_background(top_panel, libtcod.black)
    libtcod.console_clear(top_panel)
    libtcod.console_set_default_background(side_panel, libtcod.black)
    libtcod.console_clear(side_panel)
    libtcod.console_set_default_background(bottom_panel, libtcod.black)
    libtcod.console_clear(bottom_panel)

    # print the game messages, one line at a time
    y = 1
    for (line, color_msg) in game_msgs:
        libtcod.console_set_default_foreground(bottom_panel, color_msg)
        libtcod.console_print_ex(bottom_panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # show the player's stats
    gui.render_hp_bar(bottom_panel, 1, 1, BAR_WIDTH, 'HP', player.entclass.hp, player.entclass.max_hp)
    # shows exp
    gui.render_exp_bar(bottom_panel, 1, 3, BAR_WIDTH, 'XP', player.entclass.xp, player.entclass.level * 10)
    # shows the time
    calc_time()
    gui.render_timeLine(top_panel, 0, 0, BAR_WIDTH_TOP, time, color.blue)
    # perk charge
    gui.perk_charge(side_panel, player.entclass.pots, -1, -1, -1, -1, -1, -1, -1, -1, -1)

    # display names of objects under the mouse
    libtcod.console_set_default_foreground(bottom_panel, libtcod.light_gray)
    libtcod.console_print_ex(bottom_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, '')

    # blit the contents of "panel" to the root console
    libtcod.console_blit(bottom_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_BOTTOM)
    libtcod.console_blit(top_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT_TOP, 0, 0, PANEL_TOP)
    libtcod.console_blit(side_panel, 0, 0, SIDE_PANEL_WIDTH, SIDE_PANEL_HEIGHT, 0, VISUAL_WIDTH, 0)


def calc_time():
    global time, torch_radius
    global numClicks

    if numClicks % 2 == 0 and numClicks is not 0:
        time += 1

    if time is BAR_WIDTH_TOP:
        time = 0
        numClicks = 0

    if time % 8 == 0:
        if 0 <= time <= BAR_WIDTH_TOP / 2:
            print str(time % 2)
            torch_radius += 1
        else:
            print str(time % 2)
            torch_radius -= 1


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


def get_player():
    return player


def handle_keys():
    global numClicks
    # key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  # turn-based
    global player_action, game_status
    global fov_recompute
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        player_action = 'passed'
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  # exit game
        player_action = 'passed'
    if game_status == 1:
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            attackmove(0, -1)
            globalvars.player_y = player.y
            player.entclass.update_stats(time=numClicks)
            fov_recompute = True
            player_action = 'not passed'
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            attackmove(0, 1)
            globalvars.player_y = player.y
            player.entclass.update_stats(time=numClicks)
            fov_recompute = True
            player_action = 'not passed'
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            attackmove(-1, 0)
            globalvars.player_x = player.x
            player.entclass.update_stats(time=numClicks)
            fov_recompute = True
            player_action = 'not passed'
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            attackmove(1, 0)
            globalvars.player_x = player.x
            player.entclass.update_stats(time=numClicks)
            fov_recompute = True
            player_action = 'not passed'
        else:
            key_char = chr(key.c)
            player_action = 'passed'

            if key_char == 'o' and not libtcod.console_is_key_pressed(key):
                selected_option = gui.charge_menu()
                cast_spells(selected_option)

            if key_char == 'p' and not libtcod.console_is_key_pressed(key):
                # show in-game menu
                chosen_option = gui.perk_menu(
                    'Press the key next to the class of perk you want to learn. Points: ' + str(
                        player.entclass.points[1]) + '\n', 1, -1)
                if chosen_option is 0:
                    chosen_perk = gui.perk_menu('FORTITUDE.\n', 0, 0)
                    player.entclass.skill_perk(0, chosen_perk)
                elif chosen_option is 1:
                    chosen_perk = gui.perk_menu('CUNNING.\n', 0, 1)
                    player.entclass.skill_perk(1, chosen_perk)
                elif chosen_option is 2:
                    chosen_perk = gui.perk_menu('SAVAGERY.\n', 0, 2)
                    player.entclass.skill_perk(2, chosen_perk)

            if key_char == 'u' and not libtcod.console_is_key_pressed(key):
                player.entclass.take_pot()

            if key_char == 'i' and not libtcod.console_is_key_pressed(key):
                # show black screen in game
                gui.text_menu()

            if key_char == 'x' and not libtcod.console_is_key_pressed(key):
                gui.save_game(player, objects)
                message('Game saved!')

            if key_char == 'd' and not libtcod.console_is_key_pressed(key):  # debug key
                pass



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
    global game_status
    global map
    while not libtcod.console_is_window_closed():

        # show the game's title
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

            create_game()

            return game_status
        if choice == 2:  # load last game
            try:
                gui.load_game(player, map, objects)
                print objects
            except:
                gui.msgbox('\n No saved game to load.\n', 24)
                continue
            game_status = 1

            create_game()

            return game_status
        elif choice == 3:  # quit
            return


def generate_fov_map():
    global fov_recompute
    global fov_map
    global world
    fov_recompute = True
    fov_map = libtcod.map_new(MAP_SIZE, MAP_SIZE)
    for y in range(MAP_SIZE):
        for x in range(MAP_SIZE):
            libtcod.map_set_properties(fov_map, x, y, not tile_list[world.map[x * MAP_SIZE + y]].sight_blocked,
                                       not tile_list[world.map[x * MAP_SIZE + y]].move_blocked)


def create_game():
    global tile_list
    global game_msgs
    global world
    game_msgs = []
    message('Welcome to Rogue Island!', color.yellow)
    map = loader.load_map()

    world.set_map(map)
    world.set_player(player)

    world.objects.append(player)

    globalvars.player_x = player.x
    globalvars.player_y = player.y

    make_visual_map()

    generate_fov_map()

    libtcod.console_clear(con)


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('data/fonts/terminal' + str(FONT_SIZE) + 'x' + str(FONT_SIZE) + '_gs_ro.png',
                                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Rogue Island', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

global tile_list
global game_msgs
tile_list = []

load_tiles()

global world
world = world.World(con, tile_list)

# create the entity and the object of the player
playerentity = playercharacter.PlayerEntity(hp=100, strength=5, agility=5, intelligence=5, vitality=5,
                                            first_name='Lennard', name='Cooper', race='human', gender='f',
                                            on_death=game_over)
player = Player(world, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', 'player', libtcod.white, blocks=True,
                entclass=playerentity)

if game_status == 0:
    info_text = Info_text("                                                                              ")
    generator_thread = thread.start_new_thread(island_generator.start, (MAP_SIZE, shared_percent))

if game_status == 1:
    create_game()

while not libtcod.console_is_window_closed():

    if game_status == 0:
        update_info(info_text.get())
        # print generator_thread

    libtcod.console_flush()

    if game_status == 1:
        # Add the queued game messages sent from playercharacter.py
        while len(globalvars.queued_messages) > 0:
            message(globalvars.queued_messages[0])
            globalvars.queued_messages.pop(0)
        # render the screen
        render_all()
        # erase all objects at their old locations, before they move
        for object in world.objects:
            object.clear()

        # handle keys and exit game if needed
        exit = handle_keys()

        world.manage_monsters()

        if game_status == 1 and player_action == 'not passed':
            for object in world.objects:
                if object is not None:
                    if object.entclass != None and object != player:
                        if libtcod.map_is_in_fov(fov_map, object.x, object.y):
                            object.entclass.last_coordinates = None
                            object.entclass.move_to(player)
                        else:
                            if object.entclass.last_coordinates is not None:
                                object.move_towards_tile(object.entclass.last_coordinates)
                            else:
                                object.entclass.last_coordinates = (player.x, player.y)
                                object.move_towards_tile(object.entclass.last_coordinates)

    # Menu
    if game_status == 2:
        main_menu()

    # Intro
    if game_status == 3:
        img = libtcod.image_load("data/images/intro_2.png")
        libtcod.image_blit_rect(img, 0, 0, 0, -1, -1, libtcod.BKGND_SET)
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)
