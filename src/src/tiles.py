class Tile:
    # a tile of the map and its properties
    def __init__(self, id, chars, move_blocked, sight_blocked, colors, animation_color):
        self.id = id
        self.chars = []
        self.colors = []
        self.move_blocked = move_blocked
        self.sight_blocked = sight_blocked
        self.animation_color = animation_color

        if self.chars == '':
            self.chars = '?'
        else:
            self.chars = chars.split(",")

        if self.colors == "":
            self.colors = "debug"
        else:
            self.colors = colors.split(",")
