import globalvars
import random

class Monster(object):
    def __init__(self, hp, level, agility, strength, intelligence, on_death=None, player=None):
        self.hp = hp
        self.level = level
        self.agility = agility
        self.strength = strength
        self.intelligence = intelligence
        self.on_death = on_death
        self.stunned = 0
        self.frozentomb = 0
        self.player = player
        self.dead = False
        self.last_coordinates = (0, 0)

    def take_damage(self, dmg):
        if dmg > 0:
            self.hp -= dmg

    def attack(self, target):
        if random.randint(0, self.agility) > random.randint(0, target.entclass.agility):
            damage = self.strength * random.randint(1, self.intelligence) - random.randint(0, target.entclass.strength)
        else:
            damage = self.strength - random.randint(0, target.entclass.strength)

        if damage > 0:
            target.entclass.take_damage(self, damage)
        else:
            print self.owner.name.capitalize() + ' attacks you, but without any effect.'

    def move_to(self, player, x=0, y=0):
        monster = self.owner
        if not self.dead:
            if self.hp <= 0:
                self.monster_death(player)

            else:
                if monster.entclass.frozentomb == 1:
                    monster.entclass.take_damage(player.entclass.intelligence)
                    globalvars.queued_messages.append(monster.name + ' freezes slowly until death.')
                elif monster.entclass.stunned == 0:
                    if monster.distance_to_object(player) >= 2:
                        if self.last_coordinates is None:
                            monster.move_towards_object(player)
                        else:
                            monster.move_towards_tile(self.last_coordinates)
                    elif player.entclass.hp > 0:
                        monster.entclass.attack(player)
                elif monster.entclass.stunned == 1:
                    monster.entclass.stunned = 0
                    globalvars.queued_messages.append(monster.name + ' breaks free of its confusion.')

    def monster_death(self, player):
        # Vampirism Perk
        if player.entclass.perks[1][5] == 1:
            player.entclass.hp += int(self.hp / 2)
        # Soul Reaver Stack Gain
        if player.entclass.perks[2][5] == 1:
            player.entclass.souls += 1
        self.dead = True

        player.entclass.xpInc(self.level)
