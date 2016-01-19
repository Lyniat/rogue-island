import random

class entity(object):
    def __init__(self, hp, agility, strength, intelligence, vitality, on_death=None):
        self.hp = vitality * 10
        self.agility = agility
        self.strength = strength
        self.intelligence = intelligence
        self.vitality = vitality
        self.xp = 0
        self.level = 1
        self.max_hp = vitality*10
        self.on_death = on_death
        # Array defining the available points:
        # 0: Attributes, 1: Perks
        self.points = [0, 0]
        self.perks = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0]]

    def levelUp(self):
        self.points[0] += 3
        self.points[1] += 1

    def take_damage(self, dmg):
        if dmg > 0:
            self.hp -= dmg

        if self.hp <= 0:
                function = self.on_death
                if function is not None:
                    function(self.owner)

    def attack(self, target):
        if self.agility > target.entclass.agility:
            damage = self.strength * 2 - target.entclass.strength
        else:
            damage = self.strength - target.entclass.strength

        if damage > 0:
            target.entclass.take_damage(damage)
        else:
            print self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!'

    # Controls the experience income; the more intelligent you are, the more experience you get.
    def xpInc(self, xp):
        self.xp += (xp * 0.1 * int)


"""
Explanation for the Perk Tree:
Iron Will	    Ram	            Charge		Paladin	        Pillager	    Rogue		    Soldier	    Second Strike	First Strike
Veteran's Scars	Stunning	    Deflect		Warmth	        Forager	        Vampirism		Combattant	Multistrike 	Weapon Throw
Ignore the Pain	Dungeon Basher	Hurl		Word of Power	Hand of Midas	Soulreaver		Warmonger	Enormous Blast	Flurry

Iron Will:
Veteran's Scars:
Ignore the Pain:
Ram:
Stuning:
Dungeon Basher:
Charge:
Deflect:
Hurl:
Paladin:
Warmth:
Word of Power:
Pillager:
Forager:
Hand of Midas:
Rogue:
Vampirism:
Soulreaver:
Soldier:
Combattant:
Warmonger:
Second Strike:
Multistrike:
Enormous Blast:
First Strike:
Weapon Throw:
Flurry:
"""
