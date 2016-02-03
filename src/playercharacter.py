import random

import globalvars


class PlayerEntity(object):
    def __init__(self, hp, strength, agility, intelligence, vitality, first_name, name, race, gender, on_death=None):
        self.agility = agility
        self.strength = strength
        self.intelligence = intelligence
        self.vitality = vitality
        self.hp = hp + vitality * 10
        self.xp = 0
        self.level = 1
        self.max_hp = hp + vitality * 10
        self.dmgot = 0  # dmgot stands for DoT which stands for Damage over Time. dot isn't used because of ambiguity
        self.on_death = on_death
        self.souls = 0
        self.bloodlust = 0
        self.first_name = first_name
        self.name = name
        self.race = race
        self.gender = gender
        # Array defining the available points:
        # 0: Attributes, 1: Perks
        self.points = [0, 0]
        self.perks = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0]]

    def level_up(self):
        self.points[0] += 3
        self.points[1] += 1

    def update_stats(self, time=None):
        self.max_hp == self.vitality * 10
        # Veteran's Scar's Perk
        if self.perks[1][0] == 1:
            self.max_hp += self.strength * 5
        # Warmth Perk
        if self.perks[1][3] and self.hp < self.max_hp and time is not None and 19 < time < 57:
            self.hp += 1
        # Iron Will Perk
        if self.perks[0][0] == 1 and self.hp <= 0:
            self.hp -= 1
        # Soul Reaver Perk Decay and Gain on time
        if self.perks[2][5] == 1:
            if time == 1:
                self.souls += 1
                globalvars.queued_messages.append(
                    'It is midnight. You gain one soul. You now have ' + str(self.souls) + ' souls.')
            elif time == 37:
                self.souls -= 5
                globalvars.queued_messages.append(
                    'It is midnight. You lose five souls. You now have ' + str(self.souls) + ' souls.')
            if self.souls < 0:
                self.souls = 0

    def take_damage(self, source, dmg):
        enemy_name = str(source.name)
        # Warmonger Perk chance to fall in bloodlust
        if self.perks[2][6] == 1 and random.randint(0, 100) <= 10 and self.bloodlust == 0:
            globalvars.queued_messages.append('WAAAAAAAAAR! I NEED BLOOD!')
            self.bloodlust = 5
        if dmg > 0:
            # Warmonger Perk Bloodlust incoming damage increase
            if self.bloodlust > 0:
                dmg *= 2
            # deflect perk
            if self.perks[2][1] == 1 and random.randint(0, 1) == 1:
                source.take_damage(dmg)
                globalvars.queued_messages.append('You successfully retaliate ' + enemy_name + '\'s attack!')
            # Ignore the Pain perk chance to transform into dot
            if self.perks[2][0] == 1 and random.randint(0, 100) <= 20:
                self.dmgot = dmg
                globalvars.queued_messages.append('You are attacked by ' + enemy_name + ', but you ignore the pain.')
            else:
                self.hp -= dmg
                globalvars.queued_messages.append('You take ' + str(dmg) + ' damage from' + enemy_name + '.')
            if self.perks[0][8] == 1:
                source.take_damage(self.agility)
                globalvars.queued_messages.append(
                    'You quickly slice against ' + enemy_name + ' for ' + str(self.agility) + ' damage.')
        # Ignore the Pain perk ongoing DoT
        if self.dmgot > 0:
            if self.dmgot % 3 == 0:
                self.hp -= self.dmgot / 3
                self.dmgot -= self.dmgot / 3
                globalvars.queued_messages.append(
                    'You start to feel the pain, and suffer ' + str(self.dmgot / 3) + ' damage.')
            elif self.dmgot % 3 >= 3:
                self.hp -= (self.dmgot - self.dmgot % 3) / 3
                self.dmgot -= (self.dmgot - self.dmgot % 3) / 3
                globalvars.queued_messages.append(
                    'You start to feel the pain, and suffer ' + str((self.dmgot - self.dmgot % 3) / 3) + ' damage.')
            else:
                self.hp -= self.dmgot
                self.dmgot = 0
                globalvars.queued_messages.append(
                    'You start to feel the pain, and suffer ' + str(self.dmgot) + ' damage. The pain wears off.')

        if self.hp <= 0 and self.perks[0][0] == 0 or self.hp <= -10 and self.perks[0][0] == 1:
            self.on_death(self)

    def attack(self, target, time=None):
        enemy_name = str(target.name)
        if random.randint(0, self.agility) > random.randint(0, target.entclass.agility):
            damage = self.strength * random.randint(1, self.intelligence) - random.randint(0, target.entclass.strength)
        else:
            damage = self.strength - random.randint(0, target.entclass.strength)

        # Ram Perk
        if self.perks[1][0] == 1:
            damage += self.vitality
        # Soldier Perk
        if self.perks[0][7] == 1:
            damage += self.agility
        # Paladin Perk
        if self.perks[0][3] == 1 and 19 < time < 57:
            damage += self.strength
        # Rogue Perk
        if self.perks[0][3] == 1 and not 19 < time < 57:
            damage += self.agility
        # Multi Strike Perk
        if self.perks[1][7] == 1:
            if globalvars.monster_proximity_block[1] == 1 and globalvars.monster_proximity_block[3] == 1:
                damage *= 2
        # Dungeon Basher Perk
        if self.perks[2][1] == 1:
            x = target.x - globalvars.player_x
            y = target.y - globalvars.player_y

            if y == -1 and globalvars.monster_proximity_block[0] == 1:
                damage *= 2
            elif x == 1 and globalvars.monster_proximity_block[1] == 1:
                damage *= 2
            elif y == 1 and globalvars.monster_proximity_block[2] == 1:
                damage *= 2
            elif x == -1 and globalvars.monster_proximity_block[3] == 1:
                damage *= 2
            else:
                target.move(2 * x, 2 * y)

        # Soulreaver Perk damage addition
        if self.perks[2][5] == 1:
            damage += self.souls
        # Stunning Perk
        if self.perks[1][1] == 1 and random.randint(0, 100) <= 20:
            target.entclass.stunned = 1
            globalvars.queued_messages.append('You have overwhelmed ' + enemy_name + ', stunning it.')
        # Bloodlust Perk
        if self.bloodlust > 0:
            damage *= 4
            self.bloodlust -= 1
            if self.bloodlust == 0:
                globalvars.queued_messages.append('Your thirst for blood has been quenched.')
        if damage > 0:
            target.entclass.take_damage(damage)
            globalvars.queued_messages.append('You attack ' + enemy_name + '  for ' + str(damage) + '.')
        else:
            pass

    # Controls the experience income; the more intelligent you are, the more experience you get.
    def xpInc(self, xp):
        self.xp += (xp * int(self.intelligence / 2))

        if self.xp > 10 * self.level:
            globalvars.queued_messages.append('You have levelled up! (\'P\' for perks)')
            self.level_up()
            self.xp -= self.level * 10

    def skill_perk(self, perkclass, perk):
        if self.points[1] > 0:
            if perkclass == 0:
                if perk == 0:
                    self.perks[0][0] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You have learnt how to cheat death.')
                if perk == 1:
                    if self.perks[0][0] == 1:
                        self.perks[1][0] = 1
                        self.points[1] -= 1
                    globalvars.queued_messages.append('Your scars strengthen your body.')
                if perk == 2:
                    if self.perks[1][0] == 1:
                        self.perks[2][0] = 1
                        self.points[1] -= 1
                    globalvars.queued_messages.append('You have learnt to ignore pain!')
                if perk == 3:
                    self.perks[0][1] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You ram your enemies from now on.')
                if perk == 4:
                    if self.perks[0][1] == 1:
                        self.perks[1][1] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You can stun your enemies now.')
                if perk == 5:
                    if self.perks[2][1] == 1:
                        self.perks[2][1] == 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You can push your enemies back with sheer force.')
                if perk == 6:
                    self.perks[0][2] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You can now charge to your enemies!')
                if perk == 7:
                    if self.perks[0][2] == 1:
                        self.perks[1][2] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You sometimes reflect any incoming damage.')
                if perk == 8:
                    if self.perks[1][2] == 1:
                        self.perks[2][2] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You can throw your enemies around!')
            if perkclass == 1:
                if perk == 0:
                    self.perks[0][3] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You deal more damage at day!')
                if perk == 1:
                    if self.perks[0][3] == 1:
                        self.perks[1][3] = 1
                        self.points[1] -= 1
                    globalvars.queued_messages.append('You slowly regenerate life at day.')
                if perk == 2:
                    if self.perks[1][3] == 1:
                        self.perks[2][3] = 1
                        self.points[1] -= 1
                    globalvars.queued_messages.append('You can call forth a powerful blast of energy!')
                if perk == 3:
                    self.perks[0][4] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You can create homing Arcane Missiles.')
                if perk == 4:
                    if self.perks[0][4] == 1:
                        self.perks[1][4] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You are able to throw a devastating fireball.')
                if perk == 5:
                    if self.perks[1][4] == 1:
                        self.perks[2][4] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You can suck all warmth out of a foe\'s body.')
                if perk == 6:
                    self.perks[0][5] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You deal more damage at night.')
                if perk == 7:
                    if self.perks[0][5] == 1:
                        self.perks[1][5] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You gain life when slaying an enemy.')
                if perk == 8:
                    if self.perks[1][5] == 1:
                        self.perks[2][5] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You steal your enemy\'s souls.')
            if perkclass == 2:
                if perk == 0:
                    self.perks[0][6] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('Your attacks are faster now, resulting in more damage.')
                if perk == 1:
                    if self.perks[0][6] == 1:
                        self.perks[1][6] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('~~~NOT IMPLEMENTED~~~')
                if perk == 2:
                    if self.perks[1][6] == 1:
                        self.perks[2][6] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You feel the urge to kill rising...')
                if perk == 3:
                    self.perks[0][7] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You can attack without retaliation.')
                if perk == 4:
                    if self.perks[0][7] == 1:
                        self.perks[1][7] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('Your strikes possibly pierce your enemy.')
                if perk == 5:
                    if self.perks[1][7] == 1:
                        self.perks[2][7] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You can summon a powerful earthquake around you.')
                if perk == 6:
                    self.perks[0][8] = 1
                    self.points[1] -= 1
                    globalvars.queued_messages.append('You can sometimes retaliate an attack.')
                if perk == 7:
                    if self.perks[0][8] == 1:
                        self.perks[1][8] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('You can throw your weapon.')
                if perk == 8:
                    if self.perks[1][8] == 1:
                        self.perks[2][8] = 1
                        self.points[1] -= 1
                        globalvars.queued_messages.append('~~~NOT IMPLEMENTED~~~')


"""
Explanation for the Perk Tree:
Iron Will	    Ram	            Charge		Paladin	        Arcane Missiles Rogue		    Soldier	    Second Strike	First Strike
Veteran's Scars	Stunning	    Deflect		Warmth	        Fireball        Vampirism		Combattant	Multistrike 	Weapon Throw
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
CCharge:             You instantly charge to your enemy and attack him once. Must be in sight.
XDeflect:            You sometimes deflect incoming damage, sharing the wounds with your foe.
CHurl:               You throw your enemy. He takes massive damage in height of ten times your vitality, and appears
                    randomly somewhere within 3 tiles of you again.
XPaladin:            You are a paragon of good deeds. You deal higher damage at day, especially if against innately
                    evil monsters.
XWarmth:             You bath in the warmth of sunrays, slowly regenerating life.
CWord of Power:      You speak a Word of Power, damaging all enemies in a large radius in height of your combined
                    intelligence, strength and vitality.
CArcane Missiles:    You fire three arcane missiles at the nearest enemy from afar. You gain 3 charges every day, no
                    maximum.
                    Deals damage in height of your intelligence.
                    Regains the charge if it kills the enemy.
CFireball:           Throw a powerful fireball, damaging all in a little radius around the impact itself.
                    Deals damage in height of your intelligence.
                    You gain 3 charges every day, no maximum.
CFrozen Tomb:        Freeze a single foe until its death. It suffers damage in height of your intelligence per turn and
                    can't move. Gain one charge each day, no maximum.
XRogue:              You perform best in the shadows and the cloak of the night. You deal additional damage against all
                    foes when it is night.
XVampirism:          You feast on your enemies, regaining a tenth of your enemies health as soon as they die.
XSoul Reaver:        You posses the power to collect the souls of the dead, gaining one damage per attack for every
                    soul you have collected. You gain one soul at midnight, but lose 5 at midday.
XSoldier:           Your physical form is at its prime. Your agility now influences your damage directly, in addition
                    to your innate chance to critically strike.
Combatant:          The amount of potions you've consumed made your direly need the potions. You now lose 1 Hp per
                    round, but always gain half your maximum life back instead of flat 50.
XWarmonger:          Each time you are attacked, you have chance to fall into bloodlust. Bloodlust makes you suffer
                    double damage until your thirst for blood is quenched, but deal quadruple damage for five attacks.
CSecond Strike:      You can attack a single enemy once without retaliation. Gains one charge every 5 rounds, up to a
                    maximum of 1.
XBig Swing:          You have a small chance to take strike out, dealing double damage if there is no object or monster
                    around your target stopping the ferocious attack.
CEnormous Blast:     You stomp the ground with full force, dealing quadruple strength plus agility directly around you
                    double a tile further, and normal damage another tile further.
XFirst Strike:       Each time you are attacked, there is a chance you simultaneously retaliate and deal damagein height
                    of your agility.
CWeapon Throw:       Throw your weapon (and magically retrieve it again) dealing normal damage without chance of
                    retaliation. Gain 3 charges per day, no maximum.
CFlurry:             Your attacks become one flash. On your next attack, you have a chance of 100% to attack a second
                    time for full damage, and half the previous chance again and again until you ultimately fail to hit.
"""
