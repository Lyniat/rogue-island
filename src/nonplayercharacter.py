class monster(object):
    def __init__(self, hp, level, agility, strength, intelligence, on_death=None):
        self.hp = hp
        self.level = level
        self.agility = agility
        self.strength = strength
        self.intelligence = intelligence
        self.on_death = on_death
        self.stunned = 0

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
            target.entclass.take_damage(self, damage)
        else:
            print self.owner.name.capitalize() + ' attacks you, but without any effect.'



