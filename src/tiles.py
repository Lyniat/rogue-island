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


#################
#
# structure of tile vars
# fffeeedddccccbbaaa
#  3  3  3  4  2  3  = 18
# f = objectId, e = region details, d = biomeID, c = height, b = tileVariation, a = tileId
#
#################

#get

def get_id(self,value):
    string = str(value)
    res = string[15:]
    return int(res)

def get_tile_var(self,value):
    string = str(value)
    res = string[13:14]
    return int(res)

def get_height(self,value):
    string = str(value)
    res = string[9:12]
    return int(res)

def get_biome(self,value):
    string = str(value)
    res = string[6:8]
    return int(res)

def get_region(self,value):
    string = str(value)
    res = string[3:5]
    return int(res)

def get_object(self,value):
    string = str(value)
    res = string[:2]
    return int(res)

#add (same function as set but faster but can also used only once per tile)

def add_id(self,tile,value):
    result = tile +value
    return result

def add_tile_var(self,tile,value):
    result = tile + value*1000
    return result

def add_height(self,tile,value):
    result = tile + value*100000
    return result

def add_biome(self,tile,value):
    result = tile + value*1000000000
    return result

def add_region(self,tile,value):
    result = tile + value*1000000000000
    return result

def add_object(self,tile,value):
    result = tile + value*1000000000000000
    return result