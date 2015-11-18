class Tile:
    # a tile of the map and its properties
    def __init__(self,id, blocked, block_sight=None):
        self.blocked = blocked
        self.id = id

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
