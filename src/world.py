import random
import entitymanager

class World():
    def __init__(self, con, tile_list):
        self.con = con
        self.tile_list = tile_list
        self.objects = []
        self.entitymanager = entitymanager.Entitymanager()
        self.entitymanager.load_entities("data/entities/monsters")

    def set_map(self, map):
        self.map = map

    def set_player(self,player):
        self.player = player

    def manage_monsters(self):
        if len(self.objects) < 30:
            r = random.randrange(4)

            if r < 1:
                x = self.player.x + 80
                y = self.player.y + 80 + random.randrange(-10, 10)

            if 1 <= r < 2:
                x = self.player.x - 80
                y = self.player.y + 80 + random.randrange(-10, 10)

            if 2 <= r < 3:
                x = self.player.x + 80 + random.randrange(-10, 10)
                y = self.player.y + 80

            if 3 <= r < 4:
                x = self.player.x + 80 + random.randrange(-10, 10)
                y = self.player.y - 80

            tile_id = self.map[x * 512 + y]
            monster = self.entitymanager.get_monster_at_tile(tile_id,x,y)
            print monster
            if monster is not None:
                self.objects.append(monster)

    def is_field_blocked(self, x, y):
        MAP_SIZE = 512  # UGLY JUST FOR TESTING
        if self.tile_list[self.map[x * MAP_SIZE + y]].move_blocked == 0:
            return True
        for object in self.objects:
            if object.blocks and object.x == x and object.y == y:
                return True
        return False
