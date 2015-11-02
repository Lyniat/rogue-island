import tiles
import math


def make_map(width, height):
    global start_x, start_y
    global new_map
    new_map = [[tiles.Tile(False)
                for y in range(height)]
               for x in range(width)]
    heightmap = [[0
                  for y in range(height)]
                 for x in range(width)]

    for x in range(width):
        for y in range(height):

            # create map
            height_value = math.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)

            # strand zerfransen
            height_value -= math.fabs(math.sin(x / 3) * 2)

            height_value -= math.fabs(math.cos(y / 4) * 2)

            if height_value < width / 2.2:
                new_map[x][y].blocked = False
                new_map[x][y].block_sight = False
                start_x = x
                start_y = y
            else:
                new_map[x][y].blocked = True
                new_map[x][y].block_sight = True

    return new_map


def get_start_position():
    return [start_x, start_y]
