import math
import random

import pygame

from . import pygpen as pp
from .bullet import Bullet, QuakeBullet, SludgeBomb, WarpBullet, WarpBulletInstant, Arrow, PhaseRound, AttackAnim, Rocket, FirebombArrow
from .debris import Debris, Grenade, Nuke, ABILITY_DURATIONS
from .drops import Drop
from .smite import Smite
from .animation import Animation
from .const import WEAPON_STATS, WEAPON_NAMES, ENCHANTS, PRICE_SCALE, TYPES, raw_enchant_stat

for weapon in WEAPON_STATS:
    if 'penetration' not in WEAPON_STATS[weapon]:
        WEAPON_STATS[weapon]['penetration'] = 0

class Weapon(pp.Element):
    def __init__(self, weapon_type, owner):
        super().__init__()

        self.type = weapon_type
        self.owner = owner

        self.shoot_cooldown = [0, 1]
        self.secondary_cooldown = [0, 1]

        self.shot_count = 0

        self.attempting_fire = [False, False]
        self.last_charge = 0

        if self.type not in self.e['State'].weapon_enchants:
            self.enchants = {enchant: [0, 0] for enchant in ENCHANTS}
        else:
            self.enchants = {enchant: (self.e['State'].weapon_enchants[self.type][enchant] if enchant in self.e['State'].weapon_enchants[self.type] else [0, 0]) for enchant in ENCHANTS}

        self.animation = None
        if WEAPON_STATS[self.type]['animated']:
            self.animation = self.e['EntityDB']['weapons'].animations[self.type].copy()

        self.inaccuracy = 1

        self.reset()

    def reset(self):
        self.warp_mark = None
        self.shoot_cooldown[0] = 0
        self.secondary_cooldown[0] = 0

    def enchant(self):
        if not len(self.enchant_list):
            count = 2
            if random.random() < 0.05:
                count = 3
            for enchant in range(count):
                available_enchants = list(set(list(ENCHANTS)) - set([enchant[1] for enchant in self.enchant_list]))
                if available_enchants:
                    enchant_type = random.choice(available_enchants)
                    self.enchants[enchant_type] = [1 if enchant == 0 else 0.5, 1]
        else:
            for enchant in self.enchants:
                if self.enchants[enchant][0]:
                    self.enchants[enchant][1] += 1

        if not self.e['State'].guide_progress['enchant_purchase']:
            self.e['State'].guide_progress['enchant_purchase'] = 1

        self.save_enchants()

        if self.star_rating[0] == 'silver':
            self.e['Steamworks'].grant_achievement('silver_enchanter')
        if self.star_rating[0] == 'gold':
            self.e['Steamworks'].grant_achievement('golden_enchanter')

    def strip(self):
        # weight, level
        self.enchants = {enchant: [0, 0] for enchant in ENCHANTS}
        self.save_enchants()

    def enchant_stat(self, enchant_type):
        level = int(math.ceil(self.enchants[enchant_type][1] * self.enchants[enchant_type][0]))
        return raw_enchant_stat(enchant_type, level)
        
    def save_enchants(self):
        self.e['State'].weapon_enchants[self.type] = {enchant: self.enchants[enchant] for enchant in  self.enchants if self.enchants[enchant][0]}
        self.e['State'].save()
        
    @property
    def enchant_tier(self):
        count = len(self.enchant_list)
        max_level = max([enchant[2] for enchant in self.enchant_list]) if count else 0
        return (1.365 ** max_level) * (count if count else 2)
    
    @property
    def enchant_level(self):
        return max([enchant[2] for enchant in self.enchant_list]) if len(self.enchant_list) else 0
    
    @property
    def enchant_price(self):
        if self.e['State'].guide_progress['upgrade_purchase'] and self.e['State'].guide_progress['daisy_talked'] and (not self.e['State'].guide_progress['enchant_purchase']) and (self.e['State'].wave > 2):
            return 20
        return int(self.enchant_tier * 48 * self.e['State'].difficulty_set_stats['enchant_price'] * (1 - self.e['State'].upgrade_stat('wizards_hat')) * PRICE_SCALE['enchant'])

    @property
    def enchant_list(self):
        return sorted([(self.enchants[enchant][0], enchant, self.enchants[enchant][1]) for enchant in self.enchants if self.enchants[enchant][0]], reverse=True)

    @property
    def name(self):
        return WEAPON_NAMES[self.type]
    
    @property
    def title(self):
        if len(self.enchant_list):
            return f'{ENCHANTS[self.enchant_list[0][1]]["title"]} {WEAPON_NAMES[self.type]}'
        return self.name

    @property
    def chargable_primary(self):
        return self.type in {'bow', 'ember'}

    @property
    def chargable_secondary(self):
        return self.type in {'bow', 'ember'}

    @property
    def firerate(self):
        if self.owner.friendly:
            cheer_scale = 1.0
            if self.owner.alt_weapon:
                cheer_scale = self.owner.alt_weapon.enchant_stat('cheer') + 1
            return WEAPON_STATS[self.type]['firerate'] * (1.08 ** self.upgrade_stacks('extra_rounds')) * (1.65 if self.e['State'].effect_active('extra_rounds') else 1) * (self.e['State'].upgrade_stat('turret') + 1) * cheer_scale
        else:
            return WEAPON_STATS[self.type]['firerate']
    
    @property
    def projectile_spawn_locs(self):
        spawn_locs = [self.owner.gun_center]
        if self.e['State'].effect_active('double_barrel') and (self.owner == self.e['Game'].player):
            spawn_locs = [pp.utils.game_math.advance(list(self.owner.gun_center), self.owner.angle + math.pi / 2, 2.5), pp.utils.game_math.advance(list(self.owner.gun_center), self.owner.angle - math.pi / 2, 2.5)]
        return spawn_locs
    
    @property
    def img(self):
        if self.animation:
            return self.animation.img
        return self.e['Assets'].images['weapons'][self.type]
    
    @property
    def base_color(self):
        return 'blue' if self.owner.friendly else 'red'

    @property
    def num_shots(self):
        ws = WEAPON_STATS[self.type]
        shots = ws['shots']
        if random.random() < self.enchant_stat('overload'):
            shots *= 2
        return shots
    
    @property
    def max_range(self):
        ws = WEAPON_STATS[self.type]
        return ws['range'] * 350 * (1.1 ** self.e['State'].owned_upgrades['scoped_weapons'])
    
    def upgrade_stacks(self, upgrade_id):
        return self.e['State'].owned_upgrades[upgrade_id] if self.owner.friendly else 0
    
    def spawn_shell(self):
        new_debris = Debris('shell', self.owner.center, random.random() * 0.4 + 0.7)
        new_debris.v_speed *= 0.5
        new_debris.angle = self.owner.angle + math.pi + (random.random() - 0.5)
        self.e['EntityGroups'].add(new_debris, 'vfx')
    
    def update(self, dt):
        self.shoot_cooldown[0] = max(0, self.shoot_cooldown[0] - self.e['Window'].dt)
        self.secondary_cooldown[0] = max(0, self.secondary_cooldown[0] - self.e['Window'].dt)

        if self.type == 'moneygun':
            if not self.e['State'].scrap:
                self.shoot_cooldown = [99999, 99999]

        if self.attempting_fire[0]:
            if self.chargable_primary:
                self.animation.update(self.firerate * self.e['Window'].dt)
                self.last_charge = 0
                if self.animation.finished:
                    if self.owner == self.e['Game'].player:
                        self.owner.attack_hook()
                    ws = WEAPON_STATS[self.type]
                    if ws['primary'] == 'arrow_shoot':
                        for loc in self.projectile_spawn_locs:
                            for shot in range(self.num_shots):
                                self.e['EntityGroups'].add(Arrow(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], piercing=ws['penetration'], custom_projectile='arrow', src_weapon=self), 'entities')

                        self.e['Sounds'].play(ws['shot_sound'], volume=0.5)
                    if ws['primary'] == 'flaming_arrow':
                        for loc in self.projectile_spawn_locs:
                            for shot in range(self.num_shots):
                                new_arrow = Arrow(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], piercing=ws['penetration'], custom_projectile='arrow', src_weapon=self)
                                new_arrow.flaming = True
                                self.e['EntityGroups'].add(new_arrow, 'entities')

                        self.e['Sounds'].play(ws['shot_sound'], volume=0.5)
                    self.animation.reset()
        elif self.attempting_fire[1]:
            if self.chargable_secondary:
                self.animation.update(self.firerate * self.e['Window'].dt)
                self.last_charge = 1
        elif self.chargable_primary or self.chargable_secondary:
            if self.animation.finished:
                if self.owner == self.e['Game'].player:
                    self.owner.attack_hook()
                ws = WEAPON_STATS[self.type]
                if self.last_charge == 1:
                    if ws['secondary'] == 'firebomb':
                        for loc in self.projectile_spawn_locs:
                            for shot in range(self.num_shots):
                                new_arrow = FirebombArrow(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], custom_projectile='arrow', src_weapon=self)
                                new_arrow.flaming = True
                                self.e['EntityGroups'].add(new_arrow, 'entities')
                    if ws['secondary'] == 'arrow_barrage':
                        for loc in self.projectile_spawn_locs:
                            for shot in range(11):
                                angle = (shot - 5) * 0.02
                                self.e['EntityGroups'].add(Arrow(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy + angle, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], custom_projectile='arrow', src_weapon=self), 'entities')
                        
                        self.e['Sounds'].play('arrow_fire', volume=1.0)
                    self.secondary_cooldown = [ws['secondary_cooldown'] * (0.86 ** self.upgrade_stacks('stopwatch'))] * 2
            self.animation.reset()

        if self.type == 'warpgun':
            if self.warp_mark:
                marker = self.e['Assets'].images['misc']['warp_marker']
                self.e['Renderer'].blit(marker, (self.warp_mark[0] - marker.get_width() / 2 - self.e['Game'].camera[0], self.warp_mark[1] - marker.get_height() / 2 - self.e['Game'].camera[1]), z=-5.39)

        self.attempting_fire = [False, False]
    
    def attempt_fire(self, damage_scale=1.0):
        if self.shoot_cooldown[0]:
            return False
        if self.chargable_primary:
            if not self.shoot_cooldown[0]:
                self.attempting_fire[0] = True
        elif not self.shoot_cooldown[0]:
            if self.owner == self.e['Game'].player:
                self.owner.attack_hook()

            self.shoot_cooldown = [1 / self.firerate, 1 / self.firerate]
            if self.type == 'revolver':
                if self.shot_count >= 5:
                    self.shoot_cooldown = [1 / (self.firerate * 0.15), 1 / (self.firerate * 0.15)]
                    self.shot_count = -1
                    
            if self.type == 'moneygun':
                if self.e['State'].scrap:
                    self.e['State'].scrap = max(0, self.e['State'].scrap - 1)
                else:
                    return False

            ws = WEAPON_STATS[self.type]
            if ws['primary'] == 'shoot':
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots):
                        self.e['EntityGroups'].add(Bullet(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'] * damage_scale, speed=ws['speed'], piercing=ws['penetration'], src_weapon=self), 'entities')
                    self.spawn_shell()

                self.e['Sounds'].play(ws['shot_sound'], volume=0.25)
        
            if ws['primary'] == 'goofy_shot':
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots):
                        bullet = Bullet(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'] * damage_scale, speed=ws['speed'], piercing=ws['penetration'], src_weapon=self)
                        bullet.goofy_shot = True
                        self.e['EntityGroups'].add(bullet, 'entities')
                    self.spawn_shell()
                
                    self.e['Sounds'].play(ws['shot_sound'], volume=0.25)

            if ws['primary'] == 'rocket_launch':
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots):
                        self.e['EntityGroups'].add(Rocket(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], custom_projectile='rocket'), 'entities')
                self.e['Sounds'].play(ws['shot_sound'], volume=0.5)

            if ws['primary'] == 'spin_slash':
                animation_id = 'spin'
                if self.type == 'dagger':
                    animation_id = 'spin_small'
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots):
                        self.e['EntityGroups'].add(AttackAnim(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'] * damage_scale, speed=ws['speed'], piercing=ws['penetration'], src_weapon=self, animation=animation_id), 'entities')
                
                self.e['Sounds'].play(ws['shot_sound'], volume=0.25)

            if ws['primary'] == 'warpshot':
                copies = 2 if self.e['State'].effect_active('double_barrel') else 1
                for i in range(copies):
                    for j in range(self.num_shots):
                        angle = self.owner.angle + (i * 0.5 + j) * math.pi * 2 / self.num_shots
                        self.e['EntityGroups'].add(WarpBulletInstant(self.base_color, self.owner.gun_center, angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'] * damage_scale, speed=ws['speed'], piercing=ws['penetration'], src_weapon=self), 'entities')
                
                self.e['Sounds'].play(ws['shot_sound'], volume=0.25)

            if ws['primary'] == 'warp_mark':
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots):
                        self.e['EntityGroups'].add(WarpBullet(self.base_color, loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * self.inaccuracy, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'] * damage_scale, speed=ws['speed'], src_weapon=self), 'entities')
                
                self.e['Sounds'].play(ws['shot_sound'], volume=0.25)

            self.shot_count += 1
        return True

    def attempt_secondary(self):
        if self.secondary_cooldown[0]:
            return False
        if self.chargable_secondary:
            if not self.secondary_cooldown[0]:
                self.attempting_fire[1] = True
        elif not self.secondary_cooldown[0]:
            if self.owner == self.e['Game'].player:
                self.owner.attack_hook()

            ws = WEAPON_STATS[self.type]
            self.secondary_cooldown = [ws['secondary_cooldown'] * (0.86 ** self.upgrade_stacks('stopwatch')) * (1 - self.enchant_stat('quickcharge'))] * 2

            if self.upgrade_stacks('cleanse'):
                if not self.e['State'].effect_active('cleanse'):
                    self.e['State'].add_effect('cleanse', 4)
                    self.e['Sounds'].play('cleanse', volume=0.9)
                    self.e['EntityGroups'].add(pp.vfx.Circle(self.owner.center, velocity=250, decay=2.5, width=4, radius=0, color=(254, 252, 211), z=5980), 'vfx')
                    self.e['EntityGroups'].add(pp.vfx.Circle(self.owner.center, velocity=200, decay=1.5, width=4, radius=0, color=(114, 217, 239), z=5980), 'vfx')
                    if 'entities' in self.e['EntityGroups'].groups:
                        for entity in list(self.e['EntityGroups'].groups['entities']):
                            if issubclass(type(entity), Bullet):
                                if entity.type == 'red':
                                    if pp.game_math.distance(entity.pos, self.owner.center) < self.e['State'].upgrade_stat('cleanse'):
                                        entity.die()
                                        self.e['EntityGroups'].groups['entities'].remove(entity)

            secondary = ws['secondary']
            if secondary == 'extra_rounds':
                self.e['State'].add_effect('extra_rounds', ABILITY_DURATIONS['extra_rounds'])
                self.e['Sounds'].play('powerup', volume=0.45)

            if secondary == 'quickdraw':
                self.e['State'].notify(f'Weapons Reloaded', font='small_font')
                self.e['Game'].player.weapon.shoot_cooldown[0] = 0
                self.e['Game'].player.weapon.shot_count = 0
                if self.e['Game'].player.alt_weapon:
                    self.e['Game'].player.alt_weapon.shoot_cooldown[0] = 0
                    self.e['Game'].player.alt_weapon.shot_count = 0
                self.e['Sounds'].play('reload', volume=0.45)

            if secondary == 'piercing_round':
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots):
                        self.e['EntityGroups'].add(Bullet('blue', loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'], advance=ws['advance'], base_range=ws['range'], damage=ws['damage'] * 6, speed=ws['speed'], piercing=9999, src_weapon=self), 'entities')
                    self.spawn_shell()

                self.e['Sounds'].play('shoot', volume=0.5)
            if secondary == 'birdshot':
                for loc in self.projectile_spawn_locs:
                    for shot in range(self.num_shots * 4):
                        self.e['EntityGroups'].add(Bullet('blue', loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * 2, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], src_weapon=self), 'entities')
                    self.spawn_shell()

                self.e['Sounds'].play('shotgun_shoot', volume=0.5)

            if secondary == 'neutralize':
                for loc in self.projectile_spawn_locs:
                    for shot in range(20):
                        bullet = Bullet('blue', loc, self.owner.angle + (random.random() - 0.5) * 1.5, advance=ws['advance'], base_range=ws['range'], damage=0.5, speed=ws['speed'], src_weapon=self)
                        bullet.neutralize = True
                        self.e['EntityGroups'].add(bullet, 'entities')
                    self.spawn_shell()
                
                self.e['Sounds'].play('shotgun_shoot', volume=0.5)

            if secondary == 'grenade':
                self.e['EntityGroups'].add(Grenade(self.owner.center, pygame.Vector2(self.e['Game'].mpos) + self.e['Game'].camera.pos), 'entities')

                self.e['Sounds'].play('jump', volume=0.8)

            if secondary == 'nuke':
                self.e['EntityGroups'].add(Nuke(pygame.Vector2(self.e['Game'].mpos) + self.e['Game'].camera.pos), 'entities')

                self.e['Sounds'].play('arrow_fire', volume=0.8)

            if secondary == 'sludgebomb':
                for loc in self.projectile_spawn_locs:
                    self.e['EntityGroups'].add(SludgeBomb('brown', loc, self.owner.angle, advance=ws['advance'], base_range=ws['range'] * 2, damage=ws['damage'] * 3, speed=ws['speed'], src_weapon=self), 'entities')

                self.e['Sounds'].play('heavy_fire', volume=0.9)

            if secondary == 'quake':
                for loc in self.projectile_spawn_locs:
                    self.e['EntityGroups'].add(QuakeBullet('brown', loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * 2, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'], src_weapon=self), 'entities')

                self.e['Sounds'].play('heavy_fire', volume=0.9)

            if secondary == 'freeze':
                self.e['State'].add_effect('freeze', 4)

            if secondary == 'jokers_guise':
                if 'entities' in self.e['EntityGroups'].groups:
                    for entity in self.e['EntityGroups'].groups['entities']:
                        if type(entity) == Bullet:
                            if entity.type == 'red':
                                entity.type = 'blue'
                            elif entity.type == 'blue':
                                entity.type = 'red'
                self.e['HUD'].flash = 1
                self.e['Sounds'].play('joker_invert', volume=0.45)

            if secondary == 'guard':
                self.e['Game'].player.guard(1, 2)
                self.e['State'].add_effect('guard', 2)

            if secondary == 'deathspiral':
                self.e['State'].add_effect('deathspiral', 4)
                self.e['Sounds'].play('powerup', volume=0.45)
            
            if secondary == 'collateral':
                self.e['State'].add_effect('collateral', 4)
                self.e['Sounds'].play('powerup', volume=0.45)
            
            if secondary == 'backstep':
                angle = self.e['Game'].player.angle + math.pi
                self.e['Game'].player.roll((math.cos(angle), math.sin(angle)), free=True)

            if secondary == 'phase_round':
                for loc in self.projectile_spawn_locs:
                    self.e['EntityGroups'].add(PhaseRound('blue', loc, self.owner.angle + (random.random() - 0.5) * ws['inaccuracy'] * 2, advance=ws['advance'], base_range=ws['range'], damage=ws['damage'], speed=ws['speed'] * 0.6, piercing=4, src_weapon=self), 'entities')

                self.e['Sounds'].play('phase_shoot', volume=0.9)

            if secondary == 'dash_slash':
                player = self.e['Game'].player
                player.kb_stack.append([self.owner.angle, self.owner.base_speed * 5.5])
                player.invisible = 0.4
                player.iframes = 0.4
                if player.partner[0]:
                    player.partner[0].kb_stack.append([self.owner.angle, self.owner.base_speed * 5.5])
                    player.partner[0].invisible = 0.4
                    player.partner[0].iframes = 0.4

                self.e['State'].add_effect('dash_slash', 0.4, hidden=True)

                self.e['Sounds'].play('dash_slash', volume=0.7)

            if secondary == 'calamity':
                count = 0
                for machine in list(self.e['Machines'].machine_map.values()):
                    if machine.status_affected:
                        self.e['EntityGroups'].add(Smite(machine.pos), 'vfx')
                        count += 1
                
                if 'enemies' in self.e['EntityGroups'].groups:
                    ts = self.e['Tilemap'].tile_size
                    for entity in self.e['EntityGroups'].groups['enemies']:
                        if type(entity) == TYPES.CentipedeRig:
                            if entity.status_affected:
                                self.e['EntityGroups'].add(Smite((int(entity.center[0] // ts), int(entity.center[1] // ts))), 'vfx')
                                count += 1
                
                if 'frenemies' in self.e['EntityGroups'].groups:
                    for frenemy in self.e['EntityGroups'].groups['frenemies']:
                        if not frenemy.friendly:
                            if type(frenemy) == TYPES.Eye:
                                if frenemy.status_affected:
                                    self.e['EntityGroups'].add(Smite((int(frenemy.center[0] // ts), int(frenemy.center[1] // ts))), 'vfx')
                                    count += 1

                if not count:
                    self.e['State'].notify('No locally status affected machines to smite!', font='small_font')
                    self.e['Sounds'].play('denied', volume=0.7)

            if secondary == 'scrap_bomb':
                explosion_count = 0
                if 'entities' in self.e['EntityGroups'].groups:
                    for entity in list(self.e['EntityGroups'].groups['entities']):
                        if type(entity) == Drop:
                            entity.life = 0
                            spark_colors = [(38, 27, 46), (254, 252, 211)]
                            self.e['EntityGroups'].add(pp.vfx.Circle(entity.pos, velocity=100, decay=2.5, width=4, radius=0, color=(254, 252, 211), z=5980), 'vfx')
                            self.e['EntityGroups'].add(pp.vfx.Circle(entity.pos, velocity=250, decay=2.9, width=6, radius=0, color=(38, 27, 46), z=5978), 'vfx')
                            anim = Animation('small_explosion', entity.pos)
                            anim.flip[0] = random.choice([True, False])
                            self.e['EntityGroups'].add(anim, 'vfx')
                            for i in range(11):
                                self.e['EntityGroups'].add(pp.vfx.Spark(entity.pos, random.random() * math.pi * 2, size=(random.randint(5, 9), random.randint(1, 2)), speed=random.random() * 120 + 120, decay=random.random() * 3 + 0.5, color=random.choice(spark_colors), z=5981), 'vfx')
                            for machine in list(self.e['Machines'].machine_map.values()):
                                if pp.utils.game_math.distance(machine.center, entity.pos) < 20:
                                    machine.damage(3.5, src_weapon=self)
                            for entity in self.e['EntityGroups'].groups['enemies']:
                                if type(entity) == TYPES.CentipedeRig:
                                    if pp.utils.game_math.distance(entity.segments[0], entity.pos) < 20:
                                        entity.damage(3.5, src_weapon=self)
                            for entity in self.e['EntityGroups'].groups['entities']:
                                if type(entity) == TYPES.Frenemy:
                                    if (not entity.friendly) and (pp.utils.game_math.distance(entity.center, entity.pos) < 20):
                                        entity.damage(3.5, src_weapon=self)

                            explosion_count += 1
                if explosion_count:
                    self.e['Sounds'].play('boom', volume=0.7)
                else:
                    self.e['State'].notify('No scrap to explode!', font='small_font')
                    self.e['Sounds'].play('denied', volume=0.7)

            if secondary == 'warp':
                if self.warp_mark:
                    self.owner.pos = [self.warp_mark[0] - 4, self.warp_mark[1] - 3]
                    self.e['Sounds'].play('warp', volume=0.7)
                    for i in range(random.randint(5, 7)):
                        anim = Animation('flash', (self.owner.center[0] + random.randint(-6, 6), self.owner.center[1] + random.randint(-9, 6)))
                        anim.animation.update(random.random() * 0.6)
                        anim.flip[0] = random.choice([True, False])
                        self.e['EntityGroups'].add(anim, 'vfx')
                    spark_colors = [(74, 156, 223), (191, 60, 96), (254, 252, 211)]
                    for i in range(24):
                        self.e['EntityGroups'].add(pp.vfx.Spark(self.owner.center, random.random() * math.pi * 2, size=(random.randint(16, 20), random.randint(4, 6)), speed=random.random() * 70 + 20, decay=random.random() * 2 + 1, color=random.choice(spark_colors), z=0), 'vfx')
                else:
                    self.secondary_cooldown[0] = 0
        return True
    
    @property
    def star_rating(self):
        if self.enchant_level < 4:
            return ('bronze', self.enchant_level)
        elif self.enchant_level < 10:
            return ('silver', int((self.enchant_level - 2) // 2))
        else:
            return ('gold', int((self.enchant_level - 7) // 3))
    
    def render_stars(self, pos, group='default', z=9999):
        star_conf = self.star_rating
        for i in range(star_conf[1]):
            self.e['Renderer'].blit(self.e['Assets'].images['misc'][f'{star_conf[0]}_star'], (pos[0] + i * 4, pos[1]), group=group, z=z)
