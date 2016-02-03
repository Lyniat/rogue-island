import random
import math

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

    def set_player(self, player):
        self.player = player

    def manage_monsters(self):
        # create monsters
        if len(self.objects) < 70:
            for i in range(7):
                r = random.randint(1,4)

                if r == 1:
                    x = self.player.x + 40
                    y = self.player.y + random.randrange(-10, 10)

                if r == 2:
                    x = self.player.x - 40
                    y = self.player.y + random.randrange(-10, 10)

                if r == 3:
                    x = self.player.x + random.randrange(-10, 10)
                    y = self.player.y + 40

                if r == 4:
                    x = self.player.x + random.randrange(-10, 10)
                    y = self.player.y - 40

                tile_id = self.map[x * 512 + y]
                monster = self.entitymanager.get_monster_at_tile(self, tile_id, x, y)
                if monster is not None:
                    self.objects.append(monster)
                print 'Length Objects:' + str(len(self.objects))

        # delete monsters
        for monster in self.objects:
            distance = abs(self.player.x - monster.x)
            if distance > 93:
                self.objects.remove(monster)

            distance = abs(self.player.y - monster.y)
            if distance > 93:
                self.objects.remove(monster)


    def is_field_blocked(self, x, y):
        MAP_SIZE = 512  # UGLY JUST FOR TESTING
        if self.tile_list[self.map[x * MAP_SIZE + y]].move_blocked == 0:
            return True
        for object in self.objects:
            if object.blocks and object.x == x and object.y == y:
                return True
        return False
