import libtcodpy as libtcod
import tiles


class Rect:
    # a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def get_start_position():
    return [start_x, start_y]


def create_room(room):
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            new_map[x][y].blocked = False
            new_map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    # horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        new_map[x][y].blocked = False
        new_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    # vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        new_map[x][y].blocked = False
        new_map[x][y].block_sight = False


def make_map(width, height, max_rooms, rooms_min_size, rooms_max_size):
    global start_x, start_y

    # fill map with "blocked" tiles
    global new_map
    new_map = [[tiles.Tile(True)
                for y in range(height)]
               for x in range(width)]

    rooms = []
    num_rooms = 0

    for r in range(max_rooms):
        # random width and height
        w = libtcod.random_get_int(0, rooms_min_size, rooms_max_size)
        h = libtcod.random_get_int(0, rooms_min_size, rooms_max_size)
        # random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, width - w - 1)
        y = libtcod.random_get_int(0, 0, height - h - 1)

        # "Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)

        # run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            # this means there are no intersections, so this room is valid

            # "paint" it to the map's tiles
            create_room(new_room)

            # center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                # this is the first room, where the player starts at
                start_x = new_x
                start_y = new_y
            else:
                # all rooms after the first:
                # connect it to the previous room with a tunnel

                # center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            # finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    return new_map
