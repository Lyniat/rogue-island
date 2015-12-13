import libtcodpy as libtcod
import thread
import tiles
import island_generator
import color
from multiprocessing import Process, Queue, Value, Array
from ctypes import c_int

# actual size of the window
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 100

# size of the map
MAP_SIZE = 512

shared_var = Value(c_int)
shared_tilemap = Array('l',[range(10),range(10)])

VISUAL_WIDTH = 150
VISUAL_HEIGHT = 90

LIMIT_FPS = 120  # 120 frames-per-second maximum (for testing)

FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

game_status = 0

color_dark_wall = libtcod.Color(255, 0, 0)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)


class Info_text:
    def __init__(self,value):
        self.set(value)
    def get(self):
        return self.text
    def set(self,t):
        self.text = t

class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # move by the given amount, if the destination is not blocked
        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        # set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)


class Player(Object):
    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, VISUAL_WIDTH / 2, VISUAL_HEIGHT / 2, self.char, libtcod.BKGND_NONE)


def update_visual_map():
    for x in range(VISUAL_WIDTH):
        for y in range(VISUAL_HEIGHT):
            map_x = x + player.x - VISUAL_WIDTH / 2
            map_y = y + player.y - VISUAL_HEIGHT / 2

            if map_x < len(map) and map_y < len(map[0]):
                visual[x][y] = map[map_x][map_y]


def make_visual_map():
    global visual

    # fill map with "unblocked" tiles
    visual = [[tiles.Tile(0, False)
               for y in range(VISUAL_HEIGHT)]
              for x in range(VISUAL_WIDTH)]


def render_all():
    update_visual_map()

    global color_light_wall
    global color_light_ground

    # go through all tiles, and set their background color
    for y in range(VISUAL_HEIGHT):
        for x in range(VISUAL_WIDTH):
            id = visual[x][y].id
            if id == 0:
                # libtcod.console_set_char_background(con, x, y, color_dark_wall,libtcod.BKGND_SET)
                random = libtcod.random_get_int(0, 0, 1)
                if random == 0:
                    libtcod.console_set_default_foreground(con, color.blue)
                else:
                    libtcod.console_set_default_foreground(con, color.navy)
                libtcod.console_put_char(con, x, y, '~', libtcod.BKGND_NONE)
            if id == 2:
                # libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                # if math.sin(x%(y+1)):
                libtcod.console_set_default_foreground(con, color.green)
                # else:
                # libtcod.console_set_default_foreground(con, color.lime)
                libtcod.console_put_char(con, x, y, ',', libtcod.BKGND_NONE)
            if id == 1:
                libtcod.console_set_default_foreground(con, color.yellow)
                libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
            if id == 3:
                libtcod.console_set_default_foreground(con, color.navy)
                libtcod.console_put_char(con, x, y, '~', libtcod.BKGND_NONE)


    # draw all objects in the list
    for object in objects:
        object.draw()

    print'x: ', player.x, 'y: ', player.y

    # blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


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
        player.move(0, -1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)

    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)

    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)


def update_info(text):
    middle = SCREEN_WIDTH/2 - len(text)/2
    libtcod.console_print(0,middle, SCREEN_HEIGHT/2, text)


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('terminal8x8_gs_as.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INCOL)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'ASCII Adventure', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

# create object representing the player
player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', libtcod.white)

# the list of objects with those two
objects = [player]



# generate map (at this point it's not drawn to the screen)
info_text = Info_text("                                                                              ")
global map
#generator_thread = thread.start_new_thread(island_generator.generate_voronoi_diagram, (MAP_SIZE, info_text, map));
#biome_thread = thread.start_new_thread(island_generator.generate_biomes,(MAP_SIZE,));
# map = island_generator.generate_voronoi_diagram(MAP_SIZE,libtcod)
# biome_generator.make_map(MAP_SIZE)

island_generator.initialize(MAP_SIZE,info_text)
q = Queue()
p1 = Process(target=island_generator.generate_noise, args=(0,shared_var,shared_tilemap))
p2 = Process(target=island_generator.generate_noise, args=(1,shared_var,shared_tilemap))
p1.start()
p2.start()


# player.x = island_generator.get_start_position()[0]
# player.y = island_generator.get_start_position()[1]

# make_visual_map()
while not libtcod.console_is_window_closed():

    if game_status == 0:
        update_info(info_text.get())
        #print generator_thread

    libtcod.console_flush()

    if game_status == 1:
        # render the screen
        render_all()
        # erase all objects at their old locations, before they move
        for object in objects:
            object.clear()

        # handle keys and exit game if needed
        exit = handle_keys()
        if exit:
            break
