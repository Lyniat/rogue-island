class Tile:
    # a tile of the map and its properties
    def __init__(self,id,char, behavior, sight_blocked,color):
        self.id = id
        self.char = char
        self.behavior = behavior
        self.sight_blocked = sight_blocked
        self.color = color

        if self.char == '':
            self.char = '?'

        if self.color == "":
            self.color = "debug"

