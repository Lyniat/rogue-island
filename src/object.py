import math
import random

import color
import coordinate_transformer
import libtcodpy as libtcod


class Object:
    # A generic objecjt representing both the player and monsters, where entclass stands for entity class
    # and defines exactly whether it's a NPC or PC.
    def __init__(self, world, x, y, char, name, color, blocks=False, entclass=None):
        self.world = world
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
        self.entclass = entclass
        if self.entclass:
            self.entclass.owner = self

        self.con = world.con

    def move(self, dx, dy):
        # move by the given amount, if the destination is not blocked
        if not self.world.is_field_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self):
        if hasattr(self.entclass, 'dead') and self.entclass.dead:
            self.char = '%'
            self.color = color.maroon
            self.blocks = False
            self.entclass = None
            self.name = 'remains of ' + self.name
        # set the color and then draw the character that represents this object at its position
        (x, y) = coordinate_transformer.coordinates_map_to_console(self.x, self.y)
        libtcod.console_set_default_foreground(self.con, self.color)
        libtcod.console_put_char(self.con, x, y,
                                 self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        libtcod.console_put_char(self.con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def move_towards_object(self, object):
        dx = object.x - self.x
        dy = object.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        if math.fabs(dx) > math.fabs(dy):
            self.move(dx, 0)
        elif math.fabs(dx) < math.fabs(dy):
            self.move(0, dy)
        else:
            if random.randint(0, 1) == 1:
                self.move(dx, 0)
            else:
                self.move(0, dy)

    def move_towards_tile(self, (x, y)):
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(x / distance))
        dy = int(round(y / distance))
        if math.fabs(dx) > math.fabs(dy):
            self.move(dx, 0)
        elif math.fabs(dx) < math.fabs(dy):
            self.move(0, dy)
        else:
            if random.randint(0, 1) == 1:
                self.move(dx, 0)
            else:
                self.move(0, dy)

    def distance_to_object(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_to_tile(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
