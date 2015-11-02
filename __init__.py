import libtcodpy as libtcod
import tiles
import island_generator

# actual size of the window
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 100

# size of the map
MAP_WIDTH = 256
MAP_HEIGHT = 256

VISUAL_WIDTH = 150
VISUAL_HEIGHT = 90

LIMIT_FPS = 20  # 20 frames-per-second maximum

FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

color_dark_wall = libtcod.Color(255, 0, 0)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)
color_blue = libtcod.Color(0, 0, 255)
color_navy = libtcod.Color(0, 0, 127)
color_green = libtcod.Color(0, 127, 0)


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
    visual = [[tiles.Tile(False)
               for y in range(VISUAL_HEIGHT)]
              for x in range(VISUAL_WIDTH)]


def render_all():
    update_visual_map()

    global color_light_wall
    global color_light_ground

    # go through all tiles, and set their background color
    for y in range(VISUAL_HEIGHT):
        for x in range(VISUAL_WIDTH):
            wall = visual[x][y].blocked
            if wall:
                # libtcod.console_set_char_background(con, x, y, color_dark_wall,libtcod.BKGND_SET)
                random = libtcod.random_get_int(0, 0, 1)
                if random == 0:
                    libtcod.console_set_default_foreground(con, color_blue)
                else:
                    libtcod.console_set_default_foreground(con, color_navy)
                libtcod.console_put_char(con, x, y, '~', libtcod.BKGND_NONE)
            else:
                # libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                libtcod.console_set_default_foreground(con, color_green)
                libtcod.console_put_char(con, x, y, ',', libtcod.BKGND_NONE)

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
global map
map = island_generator.make_map(MAP_WIDTH, MAP_HEIGHT)

player.x = island_generator.get_start_position()[0]
player.y = island_generator.get_start_position()[1]

make_visual_map()

while not libtcod.console_is_window_closed():

    # render the screen
    render_all()

    libtcod.console_flush()

    # erase all objects at their old locations, before they move
    for object in objects:
        object.clear()

    # handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break
