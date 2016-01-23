import random

import globalvars


class entity(object):
    def __init__(self, hp, strength, agility, intelligence, vitality, first_name, name, race, gender, on_death=None):
        self.agility = agility
        self.strength = strength
        self.intelligence = intelligence
        self.vitality = vitality
        self.hp = hp + vitality * 10
        self.xp = 0
        self.level = 1
        self.max_hp = hp + vitality * 10
        self.dmgot = 0  # dmgot stands for DoT which stands for Damage over Time. DoT isn't used because of ambiguity
        self.on_death = on_death
        self.first_name = first_name
        self.name = name
        self.race = race
        self.gender = gender
        # Array defining the available points:
        # 0: Attributes, 1: Perks
        self.points = [0, 0]
        self.perks = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0]]

    def level_up(self):
        self.points[0] += 3
        self.points[1] += 1

    def update_stats(self):
        self.max_hp == self.vitality * 10
        # Veteran's Scar's Perk
        if self.perks[1][0] == 1:
            self.max_hp += self.strength * 5

    def take_damage(self, source, dmg):
        if dmg > 0:
            # Ignore the Pain perk chance to transform into dot
            if self.perks[2][0] == 1 and random.randint(0, 100) <= 20:
                self.dmgot = dmg
            else:
                self.hp -= dmg
            # deflect perk
            if self.perks[2][1] == 1:
                source.take_damage(dmg)
        # Ignore the Pain perk ongoing DoT
        if self.dmgot > 0:
            if self.dmgot % 3 == 0:
                self.hp -= self.dmgot / 3
                self.dmgot -= self.dmgot / 3
            elif self.dmgot % 3 >= 3:
                self.hp -= (self.dmgot - self.dmgot % 3) / 3
                self.dmgot -= (self.dmgot - self.dmgot % 3) / 3
            else:
                self.hp -= self.dmgot
                self.dmgot = 0
        # Iron Will Perk
        if self.hp <= 0 and self.perks[0][0] == 1 or self.hp <= -10 and self.perks[0][0] == 1:
            function = self.on_death
            if function is not None:
                function(self.owner)

    def attack(self, target):
        if self.agility > target.entclass.agility:
            damage = self.strength * 2 - target.entclass.strength
        else:
            damage = self.strength - target.entclass.strength
        # Ram Perk
        if self.perks[1][0] == 1:
            damage += self.vitality
        if self.perks[2][1] == 1:
            x = target.x - globalvars.player_x
            y = target.y - globalvars.player_y

            if y == -1 and globalvars.monster_proximity_block[0] == 1:
                damage *= 2
                print 'double, top'
            elif x == 1 and globalvars.monster_proximity_block[1] == 1:
                damage *= 2
                print 'double, right'
            elif y == 1 and globalvars.monster_proximity_block[2] == 1:
                damage *= 2
                print 'double, bot'
            elif x == -1 and globalvars.monster_proximity_block[3] == 1:
                damage *= 2
                print 'double, left'
            else:
                target.move(2*x, 2*y)
                print 'moved'
        if self.perks[1][1] == 1 and random.randint(0, 100) <= 20:
            target.entclass.stunned = 1
        if damage > 0:
            target.entclass.take_damage(damage)
        else:
            pass

    # Controls the experience income; the more intelligent you are, the more experience you get.
    def xpInc(self, xp):
        self.xp += (xp * 0.1 * int)


"""
Explanation for the Perk Tree:
Iron Will	    Ram	            Charge		Paladin	        Pillager	    Rogue		    Soldier	    Second Strike	First Strike
Veteran's Scars	Stunning	    Deflect		Warmth	        Forager	        Vampirism		Combattant	Multistrike 	Weapon Throw
Ignore the Pain	Dungeon Basher	Hurl		Word of Power	Hand of Midas	Soulreaver		Warmonger	Enormous Blast	Flurry

XIron Will:         You can now drop down to -10 health before dying, but lose 1 HP per round while below 0 HP.
XVeteran's Scars:   Your numerous scars strengthen your body.
                    Your strength now also increases your HP by 5 per point.
XIgnore the Pain:   You sometimes feel the damage of an attack over 5 rounds instead of instantly. If you already suffer
                    damage over time, you forget the old "pain".
XRam:               You use your massive physical form to overpower your foes.
                    Your vitality now increases your damage by 1 per point.
XStunning:           You overwhelm your enemies with such force, so that they are severely intimidated.
XDungeon Basher:     You are knocking enemies back by one tile sometimes, if the block behind them is not blocked. If
                    it is, they take tremendous extra damage instead.
Charge:             You instantly charge to your enemy and attack him once. Must be in sight.
XDeflect:            You sometimes deflect incoming damage, sharing the wounds with your foe.
Hurl:               You throw your enemy. He takes massive damage in height of ten times your vitality, and appears
                    randomly somewhere within 3 tiles of you again.
Paladin:            You are a paragon of good deeds. You deal higher damage at day, especially if against innately
                    evil monsters.
Warmth:             You bath in the warmth of sunrays, slowly regenerating life.
Word of Power:      You speak a Word of Power, damaging all enemies in a large radius in height of your combined
                    intelligence, strength and vitality.
Arcane Missiles:    You fire three arcane missiles at single enemy from afar. You gain 3 charges every day, no maximum.
                    Deals damage in height of your intelligence.
                    Regains the charge if it kills the enemy.
Fireball:           Throw a powerful fireball, damaging all foes in a little radius around the impact itself.
                    Deals damage in height of your intelligence.
                    You gain 3 charges every day, no maximum.
Frozen Tomb:        Freeze a single foe until its death. It suffers damage in height of your intelligence per turn and
                    can't move. Gain one charge each day, no maximum.
Rogue:              You perform best in the shadows and the cloak of the night. You deal additional damage against all
                    foes when it is night.
Vampirism:          You feast on your enemies, regaining a tenth of your enemies health as soon as they die.
Soul Reaver:        You posses the power to collect the souls of the dead, gaining one damage per attack for every
                    soul you have collected. You lose 1 soul at midnight, 5 at midday.
Soldier:            Your physical form is at its prime. Your agility now influences your damage directly, in addition
                    to your innate chance to critically strike.
Combatant:          The amount of potions you've consumed made your direly need the potions. You now lose 1 Hp per
                    round, but always gain half your maximum life back instead of flat 50.
Warmonger:          Each time you are attacked, you have chance to fall into bloodlust. Bloodlust makes you suffer
                    double damage for 5 rounds, but deal quadruple damage.
Second Strike:      You can attack a single enemy once without retaliation. Gains one charge every 5 rounds, up to a
                    maximum of 1.
Multistrike:        You have a small chance to strike all enemies around you. If there is only one foe, you pierce its
                    armor, dealing double damage instead.
Enormous Blast:     You stomp the ground with full force, dealing quadruple damage directly around you, double a tile
                    further, and normal damage another tile further.
First Strike:       Each time you are attacked, there is a chance you simultaneously retaliate and deal half your
                    normal damage.
Weapon Throw:       Throw your weapon (and magically retrieve it again) dealing normal damage without chance of
                    retaliation. Gain 3 charges per day, no maximum.
Flurry:             Your attacks become one flash. On your next attack, you have a chance of 100% to attack a second
                    time for full damage, and half the previous chance again and again until you ultimately fail to hit.
"""
