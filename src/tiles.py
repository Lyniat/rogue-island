class Tile:
    # a tile of the map and its properties
    def __init__(self, id, char, move_blocked, sight_blocked, color, animation_color):
        self.id = id
        self.char = char
        self.move_blocked = move_blocked
        self.sight_blocked = sight_blocked
        self.color = color
        self.animation_color = animation_color

        if self.char == '':
            self.char = '?'

        if self.color == "":
            self.color = "debug"
