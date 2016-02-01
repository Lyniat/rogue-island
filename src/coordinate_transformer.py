import globalvars

VISUAL_WIDTH = 75
VISUAL_HEIGHT = 55
VISUAL_WIDTH_OFFSET = 0
VISUAL_HEIGHT_OFFSET = 1


def coordinates_map_to_console(x, y):
    (x, y) = (
        x - globalvars.player_x + VISUAL_WIDTH / 2 + VISUAL_WIDTH_OFFSET,
        y - globalvars.player_y + VISUAL_HEIGHT / 2 + VISUAL_HEIGHT_OFFSET)
    return (x, y)


def coordinates_console_to_map(x, y):
    (x, y) = (x + globalvars.player_x + VISUAL_WIDTH / 2 - VISUAL_WIDTH_OFFSET,
              y + globalvars.player_y / 2 - VISUAL_HEIGHT_OFFSET)
    return (x, y)
