import math
import random

import pygame

from . import pygpen as pp

from .slash import Slash
from .tempterrain import TempTerrain
from .animation import Animation
from .smite import Smite
from .const import TYPES, STABLE_MACHINES, OFFSET_N9

class Bullet(pp.Element):
    def __init__(self, bullet_type, pos, angle, speed=None, advance=8, base_range=0.4, damage=1, piercing=0, src_weapon=None, custom_projectile=None):
        super().__init__()

        self.type = bullet_type
        self.pos = list(pos)
        self.angle = angle % (math.pi * 2)
        self.speed = min(speed if speed else 280, self.e['State'].difficulty_status['bullet_speed'] * 0.8 * self.e['State'].difficulty_set_stats['bullet_speed'] * (1 - self.e['State'].upgrade_stat('bullet_time')))
        self.damage = damage
        self.piercing = piercing
        self.hit_targets = set()
        self.life = 10
        self.bounces = 0
        self.src_weapon = src_weapon
        self.custom_projectile = custom_projectile
        self.hit_wall = False
        self.neutralize = False
        self.goofy_shot = False
        self.flaming = False

        if src_weapon and (random.random() < src_weapon.enchant_stat('disarm')):
            self.neutralize = True

        if self.type in {'blue', 'brown'}:
            self.bounces = self.e['State'].owned_upgrades['ricochet']
            self.speed = (speed if speed else 350) * (1.15 ** self.e['State'].owned_upgrades['winged_bullets'])
            self.life = (base_range * (350 / self.speed)) * (1.1 ** self.e['State'].owned_upgrades['scoped_weapons'])

        if self.type == 'enemy_blue':
            self.type = 'blue'

        self.pos = pp.game_math.advance(self.pos, self.angle, advance)

        for i in range(5):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, self.angle + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=(254, 252, 211), z=0), 'vfx')

    def collision_sparks(self, angle_offset=math.pi):
        for i in range(5):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, self.angle + random.random() * 1.5 - 0.75 + angle_offset, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=(254, 252, 211), z=0), 'vfx')

    def die(self, damaged=False, angle_offset=math.pi):
        if damaged:
            self.e['EntityGroups'].add(Slash(self.pos, self.angle + random.random() - 0.5, (20, 2)), 'vfx')
        self.collision_sparks(angle_offset=angle_offset)

    def handle_events(self):
        if self.type != 'red':
            machine = self.e['Machines'].machine_by_px(self.pos)
            if machine:
                if self.attempt_damage(machine):
                    return True
            
            if 'enemies' in self.e['EntityGroups'].groups:
                for enemy in self.e['EntityGroups'].groups['enemies']:
                    if pp.utils.game_math.distance(self.pos, enemy.segments[0]) < 10:
                        if self.attempt_damage(enemy):
                            return True
            
            if 'frenemies' in self.e['EntityGroups'].groups:
                for frenemy in self.e['EntityGroups'].groups['frenemies']:
                    if (not frenemy.friendly) and (pp.utils.game_math.distance(self.pos, frenemy.pos) < frenemy.hitbox_radius):
                        if self.attempt_damage(frenemy):
                            return True
        
        if self.type == 'red':
            player = self.e['Game'].player
            if player.partner[0] and player.partner[0].health:
                if player.partner[0].rect.collidepoint(self.pos) and (not player.partner[0].rolling):
                    if self.attempt_damage(player.partner[0], friendly=False):
                        return True
            if player.hitbox.collidepoint(self.pos) and (not player.rolling):
                if self.attempt_damage(player, friendly=False):
                    return True

    def attempt_damage(self, target, friendly=True):
        dmg = self.damage
        if self.piercing < 0:
            dmg = max(0, (1 + self.piercing) * dmg)
        if target not in self.hit_targets:
            if self.src_weapon and friendly:
                if (random.random() < self.src_weapon.enchant_stat('precision')) or (random.random() < self.e['State'].upgrade_stat('magnifying_glass')):
                    dmg *= 2
                    self.e['Game'].player.play_from('critical', self.pos, volume=1.0)
                    
                if target.health < target.max_health:
                    dmg *= (self.src_weapon.enchant_stat('cracked') + 1)
                    if (type(target) == TYPES.CentipedeRig) or ((type(target) == TYPES.Machine) and (target.type != 'beacon')):
                        if random.random() < self.src_weapon.enchant_stat('execution'):
                            dmg = target.health
                            self.e['Game'].player.play_from('execute', self.pos, volume=0.7)
                if random.random() < self.src_weapon.enchant_stat('vampirism'):
                    self.e['Game'].player.heal(dmg * 0.1)
                    self.e['Sounds'].play('drain', volume=1.0)
                if self.flaming or (random.random() < self.src_weapon.enchant_stat('heat')):
                    if type(target) in {TYPES.Machine, TYPES.CentipedeRig, TYPES.Eye}:
                        target.apply_effect('flame', 4.2, src_weapon=self.src_weapon)
                if (type(target) == TYPES.Machine) and self.neutralize:
                    if target.type not in STABLE_MACHINES:
                        target.type = 'neutral'
            expected_dmg_dealt = min(dmg, target.health)
            if target.damage(dmg, src_weapon=self.src_weapon):
                target.kb_stack.append([self.angle, 100])

            if (target.health <= 0) and (expected_dmg_dealt):
                if self.goofy_shot:
                    for i in range(9):
                        self.e['EntityGroups'].add(Bullet('red', target.center, random.random() * 2 * math.pi, speed=280, advance=0), 'entities')
                if self.src_weapon and (self.src_weapon.enchant_stat('buggy') > random.random()):
                    if ('minions' not in self.e['EntityGroups'].groups) or (len(self.e['EntityGroups'].groups['minions']) < 10):
                        centipede = TYPES.CentipedeRig(self.e['Game'].player.center, friendly=True)
                        self.e['EntityGroups'].add(centipede, 'minions')

            if not dmg:
                dmg = 0.01
                
            dmg_ratio = expected_dmg_dealt / dmg
            pen = self.e['State'].upgrade_stat('penetration')
            if friendly:
                if self.src_weapon:
                    if (random.random() < 1 - (1 - self.src_weapon.enchant_stat('smite')) ** (dmg - expected_dmg_dealt)) or (self.e['State'].effect_active('thunderclap') and (not target.health)):
                        self.e['EntityGroups'].add(Smite((target.center[0] / self.e['Tilemap'].tile_size, target.center[1] / self.e['Tilemap'].tile_size)), 'vfx')
                self.piercing -= pen * dmg_ratio + (1 - pen)
            else:
                self.piercing -= 1
            if self.piercing <= -1:
                self.die(damaged=True)
                return True
            self.hit_targets.add(target)

    def update(self, dt):
        # handle movement with bounces
        movement = [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]
        self.pos[0] += movement[0]
        if self.e['Tilemap'].solid_check(self.pos, include_gaps=False):
            self.hit_wall = True
            if self.bounces:
                self.bounces -= 1
                movement[0] *= -1
                self.collision_sparks()
                self.angle = math.atan2(movement[1], movement[0])
                self.pos[0] += movement[0]
                if self.type != 'red':
                    self.e['Game'].player.play_from('ricochet', self.pos, volume=0.7)
            else:
                self.die()
                return True
        self.pos[1] += movement[1]
        if self.e['Tilemap'].solid_check(self.pos, include_gaps=False):
            self.hit_wall = True
            if self.bounces:
                self.bounces -= 1
                movement[1] *= -1
                self.collision_sparks()
                self.angle = math.atan2(movement[1], movement[0])
                self.pos[1] += movement[1]
                if self.type != 'red':
                    self.e['Game'].player.play_from('ricochet', self.pos, volume=0.25)
            else:
                self.die()
                return True

        self.life = max(0, self.life - self.e['Window'].dt)
        if not self.life:
            self.die(angle_offset=0)
            return True
        
        for i in range(5):
            if (self.piercing > 1) and (random.random() / 30 < dt) and (self.damage > 0.9):
                self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, self.angle + math.pi + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=random.choice([(254, 252, 211), (74, 156, 223)]), z=0), 'vfx')
            if self.flaming and (random.random() / 30 < dt):
                self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, self.angle + math.pi + random.random() * 1.5 - 0.75, size=(random.randint(3, 4), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=random.choice([(254, 252, 211), (238, 209, 108), (228, 103, 71), (191, 60, 96)]), z=0), 'vfx')

        return self.handle_events()
    
    @property
    def z(self):
        return self.pos[1] / self.e['Tilemap'].tile_size + 9

    def renderz(self, offset=(0, 0), group='default'):
        if self.e['Game'].camera.rect_exp.collidepoint(self.pos):
            visibility_img = None
            if self.custom_projectile:
                img = pygame.transform.rotate(self.e['Assets'].images['projectiles'][self.custom_projectile], -math.degrees(self.angle))
            else:
                base_type = self.type
                if self.bounces and (base_type == 'red'):
                    base_type = 'purple'
                img_type = base_type
                if (img_type == 'red') and self.e['Settings'].bullet_outline:
                    img_type += '_outlined'
                img = self.e['Assets'].bullets[img_type][-int(round(math.degrees(self.angle)))]
                if self.type == 'red':
                    visibility_img = self.e['Assets'].bullets[base_type + '_visibility'][-int(round(math.degrees(self.angle)))]

            r_loc_no_cam = (self.pos[0] - img.get_width() // 2, self.pos[1] - img.get_height() // 2)
            r_loc = (r_loc_no_cam[0] - offset[0], r_loc_no_cam[1] - offset[1])

            if visibility_img and (not self.e['Machines'].high_life):
                marker = self.e['VisibilityMarkers'].render_big_marker(r_loc_no_cam, visibility_img, color=self.e['State'].marker_color)
                if marker:
                    self.e['Renderer'].blit(marker, r_loc, z=9999)

            self.e['Renderer'].blit(img, r_loc, group=group, z=self.z)
            shadow_img = self.e['Assets'].images['misc']['shadow_small']
            self.e['Renderer'].blit(shadow_img, (self.pos[0] - offset[0] - shadow_img.get_width() // 2, self.pos[1] - offset[1] - shadow_img.get_height() // 2 + 3), group=group, z=self.z - 1)

class Arrow(Bullet):
    pass

class FirebombArrow(Arrow):
    def die(self, damaged=False, angle_offset=math.pi):
        super().die(damaged, angle_offset)

        self.explode()

    def explode(self):
        spark_colors = [(238, 209, 108), (228, 103, 71), (38, 27, 46), (254, 252, 211), (191, 60, 96)]
        self.e['EntityGroups'].add(pp.vfx.Circle(self.pos, velocity=150, decay=2.5, width=4, radius=0, color=(254, 252, 211), z=5980), 'vfx')
        self.e['EntityGroups'].add(pp.vfx.Circle(self.pos, velocity=220, decay=2.7, width=8, radius=0, color=(228, 103, 71), z=5979), 'vfx')
        self.e['EntityGroups'].add(pp.vfx.Circle(self.pos, velocity=350, decay=2.9, width=6, radius=0, color=(38, 27, 46), z=5978), 'vfx')
        for i in range(40):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, random.random() * math.pi * 2, size=(random.randint(5, 9), random.randint(1, 2)), speed=random.random() * 120 + 120, decay=random.random() * 3 + 0.5, color=random.choice(spark_colors), z=5981), 'vfx')

        if 'frenemies' in self.e['EntityGroups'].groups:
            for frenemy in self.e['EntityGroups'].groups['frenemies']:
                if (not frenemy.friendly) and (pp.utils.game_math.distance(self.pos, frenemy.pos) < frenemy.hitbox_radius + 40):
                    frenemy.apply_effect('flame', 4.2, src_weapon=self.src_weapon)

        if 'enemies' in self.e['EntityGroups'].groups:
            for entity in self.e['EntityGroups'].groups['enemies']:
                if type(entity) == TYPES.CentipedeRig:
                    if pp.utils.game_math.distance(entity.segments[0], self.pos) < (12 * 4):
                        entity.apply_effect('flame', 4.2, src_weapon=self.src_weapon)

        for machine in list(self.e['Machines'].machine_map.values()):
            if pp.utils.game_math.distance(machine.center, self.pos) < (12 * 4):
                machine.apply_effect('flame', 4.2, src_weapon=self.src_weapon)

        self.e['Game'].player.play_from('boom', self.pos, volume=1.0)

        self.exploded = True

class Rocket(Bullet):
    def die(self, damaged=False, angle_offset=math.pi):
        super().die(damaged, angle_offset)

        self.explode()

    def explode(self):
        spark_colors = [(238, 209, 108), (228, 103, 71), (38, 27, 46), (254, 252, 211), (191, 60, 96), (38, 27, 46), (38, 27, 46)]
        self.e['EntityGroups'].add(pp.vfx.Circle(self.pos, velocity=150, decay=2.5, width=4, radius=0, color=(254, 252, 211), z=5980), 'vfx')
        self.e['EntityGroups'].add(pp.vfx.Circle(self.pos, velocity=220, decay=2.7, width=8, radius=0, color=(228, 103, 71), z=5979), 'vfx')
        self.e['EntityGroups'].add(pp.vfx.Circle(self.pos, velocity=350, decay=2.9, width=6, radius=0, color=(38, 27, 46), z=5978), 'vfx')
        for i in range(40):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, random.random() * math.pi * 2, size=(random.randint(5, 9), random.randint(1, 2)), speed=random.random() * 120 + 120, decay=random.random() * 3 + 1.5, color=random.choice(spark_colors), z=5981), 'vfx')
        for machine in list(self.e['Machines'].machine_map.values()):
            if pp.utils.game_math.distance(machine.center, self.pos) < 48:
                machine.damage(4, src_weapon=self.src_weapon)
        if 'enemies' in self.e['EntityGroups'].groups:
            for entity in self.e['EntityGroups'].groups['enemies']:
                if type(entity) == TYPES.CentipedeRig:
                    if pp.utils.game_math.distance(entity.segments[0], self.pos) < 48:
                        entity.damage(4, src_weapon=self.src_weapon)
        if 'frenemies' in self.e['EntityGroups'].groups:
            for frenemy in self.e['EntityGroups'].groups['frenemies']:
                if (not frenemy.friendly) and (pp.utils.game_math.distance(self.pos, frenemy.pos) < frenemy.hitbox_radius + 40):
                    frenemy.damage(4, src_weapon=self.src_weapon)
                        
        self.e['Game'].player.play_from('boom', self.pos, volume=1.0)

        self.exploded = True

class WarpBullet(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_valid_tile = None

    def update(self, dt):
        if not self.e['Tilemap'].solid_check(self.pos):
            self.last_valid_tile = (int(self.pos[0] // self.e['Tilemap'].tile_size), int(self.pos[1] // self.e['Tilemap'].tile_size))

        killed = super().update(dt)

        if killed and self.last_valid_tile:
            if self.src_weapon:
                self.src_weapon.warp_mark = ((self.last_valid_tile[0] + 0.5) * self.e['Tilemap'].tile_size, (self.last_valid_tile[1] + 0.5) * self.e['Tilemap'].tile_size)
        
        return killed
    
class WarpBulletInstant(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_valid_tile = None
        self.teleported = False

    def update(self, dt):
        if not self.e['Tilemap'].solid_check(self.pos):
            self.last_valid_tile = (int(self.pos[0] // self.e['Tilemap'].tile_size), int(self.pos[1] // self.e['Tilemap'].tile_size))

        killed = super().update(dt)

        if self.hit_wall:
            self.teleported = True
            if self.last_valid_tile and self.src_weapon and self.src_weapon.owner:
                self.src_weapon.owner.pos = [(self.last_valid_tile[0] + 0.5) * self.e['Tilemap'].tile_size - 4, (self.last_valid_tile[1] + 0.5) * self.e['Tilemap'].tile_size - 3]
                self.e['Sounds'].play('warp', volume=0.3)
                for i in range(random.randint(5, 7)):
                    anim = Animation('flash', (self.src_weapon.owner.center[0] + random.randint(-6, 6), self.src_weapon.owner.center[1] + random.randint(-9, 6)))
                    anim.animation.update(random.random() * 0.6)
                    anim.flip[0] = random.choice([True, False])
                    self.e['EntityGroups'].add(anim, 'vfx')
                spark_colors = [(38, 27, 46), (254, 252, 211)]
                for i in range(8):
                    self.e['EntityGroups'].add(pp.vfx.Spark(self.src_weapon.owner.center, random.random() * math.pi * 2, size=(random.randint(16, 20), random.randint(4, 6)), speed=random.random() * 70 + 20, decay=random.random() * 2 + 1, color=random.choice(spark_colors), z=0), 'vfx')
        
        return killed
    
class PhaseRound(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.radius = 12

    def handle_events(self):
        if self.type != 'red':
            tile_size = self.e['Tilemap'].tile_size
            base_loc = (int(self.pos[0] // tile_size), int(self.pos[1] // tile_size))
            for offset in OFFSET_N9:
                loc = (base_loc[0] + offset[0], base_loc[1] + offset[1])
                if loc in self.e['Machines'].machine_map:
                    machine = self.e['Machines'].machine_map[loc]
                    if self.attempt_damage(machine):
                        return True
            
            if 'enemies' in self.e['EntityGroups'].groups:
                for enemy in self.e['EntityGroups'].groups['enemies']:
                    if pp.utils.game_math.distance(self.pos, enemy.segments[0]) < 5 + self.radius:
                        if self.attempt_damage(enemy):
                            return True
            
            if 'frenemies' in self.e['EntityGroups'].groups:
                for frenemy in self.e['EntityGroups'].groups['frenemies']:
                    if (not frenemy.friendly) and (pp.utils.game_math.distance(self.pos, frenemy.pos) < frenemy.hitbox_radius + self.radius - 5):
                        if self.attempt_damage(frenemy):
                            return True

    def renderz(self, offset=(0, 0), group='default'):
        if self.e['Game'].camera.rect_exp.collidepoint(self.pos):
            points = [
                pp.game_math.advance(self.pos.copy(), self.angle, self.radius),
                pp.game_math.advance(self.pos.copy(), self.angle + math.pi / 2, self.radius),
                pp.game_math.advance(self.pos.copy(), self.angle, self.radius - 3),
                pp.game_math.advance(self.pos.copy(), self.angle - math.pi / 2, self.radius),
            ]
            for l_offset in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                color = (74, 156, 223)
                z_offset = 0
                if l_offset == (0, 0):
                    color = (254, 252, 211)
                    z_offset = 0.001
                self.e['Renderer'].renderf(pygame.draw.polygon, color, [(point[0] - offset[0] + l_offset[0], point[1] - offset[1] + l_offset[1]) for point in points], group=group, z=self.z + z_offset)
            shadow_img = self.e['Assets'].images['misc']['shadow_small']
            self.e['Renderer'].blit(shadow_img, (self.pos[0] - offset[0] - shadow_img.get_width() // 2, self.pos[1] - offset[1] - shadow_img.get_height() // 2 + 3), group=group, z=self.z - 1)

class SludgeBomb(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_valid_tile = None

        self.effect_range = 4

    def update(self, dt):
        if not self.e['Tilemap'].solid_check(self.pos):
            self.last_valid_tile = (int(self.pos[0] // self.e['Tilemap'].tile_size), int(self.pos[1] // self.e['Tilemap'].tile_size))

        killed = super().update(dt)

        spark_colors = [(193, 159, 113), (149, 86, 68), (106, 51, 60)]
        for i in range(5):
            if random.random() / 60 < dt:
                self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, self.angle + math.pi + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=random.choice(spark_colors), z=0), 'vfx')

        if killed and self.last_valid_tile:
            base = (int(self.pos[0] // self.e['Tilemap'].tile_size), int(self.pos[1] // self.e['Tilemap'].tile_size))
            for i in range(self.effect_range * 2 + 1):
                for j in range(self.effect_range * 2 + 1):
                    x = i - self.effect_range
                    y = j - self.effect_range
                    loc = (base[0] + x, base[1] + y)
                    # the -0.5 increases odds heavily near the center
                    dis = max(0, pp.game_math.distance((0, 0), (x, y)) - 0.5)
                    dis_ratio = dis / (self.effect_range * math.sqrt(2))
                    if random.random() < (1 - dis_ratio) ** 2:
                        self.e['EntityGroups'].add(TempTerrain((1, 0), loc), 'entities')
            self.e['Game'].player.play_from('small_boom', self.pos, volume=0.5)

        return killed

class QuakeBullet(Bullet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_valid_tile = None

        self.effect_range = 3

    def update(self, dt):
        if not self.e['Tilemap'].solid_check(self.pos):
            self.last_valid_tile = (int(self.pos[0] // self.e['Tilemap'].tile_size), int(self.pos[1] // self.e['Tilemap'].tile_size))

        killed = super().update(dt)

        spark_colors = [(193, 159, 113), (149, 86, 68), (106, 51, 60)]
        for i in range(5):
            if random.random() / 60 < dt:
                self.e['EntityGroups'].add(pp.vfx.Spark(self.pos, self.angle + math.pi + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=random.choice(spark_colors), z=0), 'vfx')

        if killed and self.last_valid_tile:
            base = (int(self.pos[0] // self.e['Tilemap'].tile_size), int(self.pos[1] // self.e['Tilemap'].tile_size))
            for i in range(self.effect_range * 2 + 1):
                for j in range(self.effect_range * 2 + 1):
                    x = i - self.effect_range
                    y = j - self.effect_range
                    loc = (base[0] + x, base[1] + y)
                    # the -0.5 increases odds heavily near the center
                    dis = max(0, pp.game_math.distance((0, 0), (x, y)) - 0.5)
                    dis_ratio = dis / (self.effect_range * math.sqrt(2))
                    if random.random() < (1 - dis_ratio) ** 2:
                        self.e['EntityGroups'].add(TempTerrain((0, 0), loc), 'entities')
            self.e['Game'].player.play_from('small_boom', self.pos, volume=0.5)

        return killed

def aoe_friendly_attack_range(pos, radius):
    targets = []
    e = pp.elements
    tile_radius = math.ceil(28 / e['Tilemap'].tile_size)
    tile_loc = (int(pos[0] // e['Tilemap'].tile_size), int(pos[1] // e['Tilemap'].tile_size))
    for x in range(tile_radius * 2 + 1):
        rel_x = x - tile_radius
        for y in range(tile_radius * 2 + 1):
            rel_y = y - tile_radius
            loc = (tile_loc[0] + rel_x, tile_loc[1] + rel_y)
            if loc in e['Machines'].machine_map:
                machine = e['Machines'].machine_map[loc]
                if pp.game_math.distance(machine.center, pos) <= radius + 5:
                    targets.append(machine)
    
    if 'enemies' in e['EntityGroups'].groups:
        for enemy in e['EntityGroups'].groups['enemies']:
            if pp.utils.game_math.distance(pos, enemy.segments[0]) < 5 + radius:
                targets.append(enemy)
    
    if 'frenemies' in e['EntityGroups'].groups:
        for frenemy in e['EntityGroups'].groups['frenemies']:
            if (not frenemy.friendly) and (pp.utils.game_math.distance(pos, frenemy.pos) < 5 + radius):
                targets.append(frenemy)
    return targets
    
class AttackAnim(Bullet):
    def __init__(self, *args, **kwargs):
        self.animation_id = kwargs['animation']
        del kwargs['animation']

        super().__init__(*args, **kwargs)

        self.owner = self.src_weapon.owner

        self.anim = Animation(self.animation_id, self.pos)

        self.time = 0

        self.radius = 28
        if self.animation_id == 'spin_small':
            self.radius = 17

    def handle_events(self):
        for target in aoe_friendly_attack_range(self.pos, self.radius):
            self.attempt_damage(target)
    
    def update(self, dt):
        self.anim.pos = self.owner.gun_center
        self.pos = self.owner.gun_center

        self.time += dt

        if self.animation_id in {'spin', 'spin_small'}:
            # set owner angle based on attack progress
            main_duration = 0.255 * (15 / 22)
            if self.time < main_duration:
                self.owner.angle = self.angle + math.pi * 2 * (self.time / main_duration)
            else:
                self.owner.angle = self.angle
        
        self.handle_events()

        killed = self.anim.update(dt)

        return killed
    
    def renderz(self, offset=(0, 0), group='default'):
        self.anim.renderz(offset=offset, group=group)