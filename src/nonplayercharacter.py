class monster(object):
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

    def take_turn(self):
        monster = self.owner
        if monster.entclass.frozentomb == 1:
            monster.entclass.take_damage(player.entclass.intelligence)
            message(monster.name + ' freezes slowly until death.')
        elif monster.entclass.stunned == 0:
            if monster.distance_to_object(player) >= 2:
                monster.move_towards(player)
            elif player.entclass.hp > 0:
                monster.entclass.attack(player)
        elif monster.entclass.stunned == 1:
            monster.entclass.stunned = 0
            message(monster.name + ' breaks free of its confusion.')



