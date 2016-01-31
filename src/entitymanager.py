import json
import os
import random
import nonplayercharacter
import object as Object
import color


class Entitymanager():
    def __init__(self):
        self.monster_dict = {}

    def load_entities(self, path):
        for file in os.listdir(path):
            if not file.endswith('.json'):
                continue
            with open(path + "/" + file, 'r') as content_file:
                content = content_file.read()

            values = json.loads(content)
            biomes = values.get("Biomes")

            for i in range(len(biomes)):
                if self.monster_dict.get(biomes[i]) is None:
                    self.monster_dict[biomes[i]] = []

            self.monster_dict[biomes[i]].append(values)

    def get_monster_at_tile(self, tile_id,x,y):
        monster_list = self.monster_dict.get(tile_id)
        if monster_list is None:
            return None

        r = random.randint(0, len(monster_list) - 1)
        monster_values = monster_list[r]
        monster_attributes = monster_values.get("Attributes")
        print monster_attributes
        # return monster

        monsterentity = nonplayercharacter.monster(hp=monster_attributes.get("HP"),
                                                   agility=monster_attributes.get("Agility"),
                                                   strength=monster_attributes.get("Strength"),
                                                   intelligence=monster_attributes.get("Intelligence"),
                                                   level=1)
        monster = Object(x, y, monster_values.get("Char"), monster_values.get("Name"),
                         getattr(color, monster_values.get("Color")),
                         blocks=True, entclass=monsterentity, ai=monsterBasicAi, player=player)

        print "monster: " + str(monster)
        return monster
