import time
import math
import random

import pygame

from . import pygpen as pp

from .bullet import Bullet
from .laser import Laser
from .rig import CentipedeRig
from .drops import Drop
from .debris import Debris, AbilityDrop, Bomb
from .animation import Animation
from .attack_circle import AttackCircle
from .automata import Automata
from .frenemy import Frenemy
from .tempterrain import TempTerrain
from .eye import Eye
from .effects import EntityEffects
from .const import FRENEMY_LEVELS, DEMO, TYPES, STABLE_MACHINES, OFFSET_N8, OBTAINABLE_POWERUPS, FRIENDLY_MACHINES

MACHINE_TYPES = ['cube', 'cylinder', 'egg', 'crab', 'bishop', 'volcano', 'bouncer', 'sniper', 'neutral', 'spawner', 'beacon', 'eye']
WEIGHTED_MACHINE_TYPES = ['cube', 'cube', 'cylinder', 'egg', 'crab', 'crab', 'bishop', 'volcano', 'bouncer', 'sniper', 'neutral', 'spawner', 'beacon']
MACHINE_ID = {machine: i + 100 for i, machine in enumerate(MACHINE_TYPES)}
MACHINE_ID['beacon'] = 255
MACHINE_ID['chest'] = 254
MACHINE_ID['spawner'] = 253
MACHINE_ID['stump'] = 252
INV_MACHINE_ID = {v: k for k, v in MACHINE_ID.items()}

EVENT_NAMES = {
    'summer': 'HighLife',
    'fall': 'Brian\'s Migraine',
    'winter': 'Blursed Blob',
}

MACHINE_OFFSETS = {
    'crab': (0, -3),
    'cube': (0, -5),
    'cylinder': (0, -6),
    'egg': (0, -2),
    'beacon': (0, -4),
    'bishop': (0, -7),
    'volcano': (0, -2),
    'chest': (0, -5),
    'stump': (-1, -3),
    'spawner': (0, -8),
    'bouncer': (0, -3),
    'sniper': (0, -5),
    'neutral': (0, -2),
}

PATTERN_DIFFICULTY = {
    'beacon': 2,
    'blinker': 1,
    'tub': 1,
    'glider': 3,
    'lwss': 4,
    'mwss': 5,
    'glider_gun': 10,
    'brain_1': 12,
    'brain_2': 5,
    'brain_3': 6,
    'blobell_windmill': 3,
    'blobell_square': 1.5,
    'blobell_cross': 1.5,
    'blobell_ball': 5,
    'blobell_blinker': 5,
    'blobell_owl': 13,
    'blobell_mask': 18,
    'ld_1': 10,
    'ld_2': 7,
}

SEASON_PATTERNS = {
    'summer': ['beacon', 'blinker', 'tub', 'glider', 'lwss', 'mwss', 'glider_gun'],
    'fall': ['brain_1', 'brain_2', 'brain_3'],
    'winter': ['blobell_ball', 'blobell_blinker', 'blobell_cross', 'blobell_owl', 'blobell_mask', 'blobell_square', 'blobell_windmill'],
    'void': ['ld_1', 'ld_2', 'lwss', 'mwss', 'glider', 'blinker'],
}

ENEMY_MACHINES = list(set(MACHINE_TYPES) - FRIENDLY_MACHINES)

MINOR_PATTERNS = {
    'summer': ['beacon', 'blinker', 'tub', 'glider', 'lwss'],
    'fall': ['brain_3', 'brain_2'],
    'winter': ['blobell_windmill', 'blobell_square', 'blobell_cross', 'blobell_ball', 'blobell_blinker'],
    'void': ['beacon', 'blinker', 'tub', 'glider', 'lwss'],
}

NEIGHBOR_9 = [(0, 0), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1), (1, 1), (-1, 1)]
NEIGHBOR_8 = [(1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1), (1, 1), (-1, 1)]

CHEST_REWARDS = ['scrap'] * 6 + OBTAINABLE_POWERUPS

class Machine:
    def __init__(self, parent, machine_type, pos, green=255, ghosted=False):
        self.parent = parent
        self.type = machine_type
        self.pos = pos

        self.timer = 0
        self.effects = EntityEffects(self)

        self.health = 3
        if self.type == 'egg':
            self.health = 1
        elif self.type == 'beacon':
            self.health = (self.parent.e['State'].wave * 2 + 20) * 3
        elif self.type == 'spawner':
            self.health = 12
        elif self.type == 'bouncer':
            self.health = 4
        elif self.type == 'sniper':
            self.health = 2
        elif self.type == 'stump':
            self.health = 9

        self.health *= 1 + ((max(0, self.parent.e['State'].wave - 1) // 40) * 0.5)

        if self.parent.e['State'].season == 'winter':
            self.health *= 2
        elif self.parent.e['State'].season == 'void':
            self.health *= 1.5

        if self.type not in FRIENDLY_MACHINES:
            self.health *= self.parent.e['State'].difficulty_set_stats['enemy_health']

        self.max_health = self.health
        self.hurt = 0

        self.alive_for = 0
        if self.pos in self.parent.last_machine_map:
            self.alive_for = 1

        self.size = [0, 0]

        if time.time() - self.parent.wave_start > 2:
            tile_size = self.parent.e['Tilemap'].tile_size
            rect = pygame.Rect(self.pos[0] * tile_size, self.pos[1] * tile_size, tile_size, tile_size)
            if self.parent.e['Game'].player.hitbox.colliderect(rect):
                if self.parent.e['Game'].player.damage(1):
                    self.parent.e['Game'].player.kb_stack.append([math.pi / 2, 100])

        self.parent.minimap.set_at(self.pos, (254, 252, 211))
        if self.type in STABLE_MACHINES:
            if self.type == 'stump':
                self.parent.minimap.set_at(self.pos, (100, 97, 139))
            elif self.type == 'chest':
                self.parent.minimap.set_at(self.pos, (228, 103, 71))
            else:
                self.parent.minimap.set_at(self.pos, (125, 43, 88))

        self.green_stat = green
        
        self.ghosted = ghosted

    def copy(self):
        new_machine = Machine(self.parent, self.type, self.pos, green=self.green_stat)
        new_machine.health = self.health
        new_machine.max_health = self.max_health
        new_machine.effects = self.effects.copy(new_machine)
        return new_machine

    def destroy(self, src_weapon=None, silent=False):
        if self.pos in self.parent.machine_map:
            del self.parent.machine_map[self.pos]
        self.parent.minimap.set_at(self.pos, (0, 0, 0))
        self.parent.e['State'].score += 1

        if not silent:
            if self.type == 'beacon':
                self.parent.e['Game'].freeze_stack.append([0.1, 1])
                for i in range(15 + int(self.parent.e['State'].wave * 1.8)):
                    self.parent.e['EntityGroups'].add(Drop('scrap', self.center), 'entities')
            
            if src_weapon:
                if self.parent.e['State'].upgrade_stat('shockwave'):
                    ignited = False
                    for offset in OFFSET_N8:
                        loc = (self.pos[0] + offset[0], self.pos[1] + offset[1])
                        if loc in self.parent.machine_map:
                            if random.random() < self.parent.e['State'].upgrade_stat('shockwave'):
                                self.parent.machine_map[loc].apply_effect('flame', 4.2, src_weapon=src_weapon)
                                ignited = True
                    if ignited:
                        self.parent.e['EntityGroups'].add(pp.vfx.Circle(self.center, velocity=100, decay=2.5, width=4, radius=0, color=(228, 103, 71), z=5980), 'vfx')
                        self.parent.e['EntityGroups'].add(pp.vfx.Circle(self.center, velocity=250, decay=2.9, width=6, radius=0, color=(238, 209, 108), z=5978), 'vfx')

        for i in range(20):
            self.parent.e['EntityGroups'].add(pp.vfx.Spark(self.center, random.random() * math.pi * 2, size=(random.randint(5, 7), 1), speed=random.random() * 120 + 120, decay=random.random() * 4 + 2, color=random.choice([(254, 252, 211), (38, 27, 46)]), z=0), 'vfx')

        if self.type == 'egg':
            if random.random() >= self.parent.e['State'].upgrade_stat('bug_spray'):
                count = 0
                if 'enemies' in self.parent.e['EntityGroups'].groups:
                    for entity in self.parent.e['EntityGroups'].groups['enemies']:
                        if type(entity) == CentipedeRig:
                            count += 1
                if count < 10:
                    self.parent.e['EntityGroups'].add(CentipedeRig(self.center), 'enemies')
        elif self.type == 'chest':
            for i in range(random.randint(3, 5)):
                self.parent.e['EntityGroups'].add(Debris('plank', self.center), 'vfx')
            count = 1
            if src_weapon and (random.random() < src_weapon.enchant_stat('treasurehunter')):
                count = 2
            if self.parent.e['State'].upgrade_stat('gamblers_dice'):
                if random.random() <= 0.5:
                    count *= 2
                else:
                    self.parent.e['State'].add_effect('miasma', 11)
            for i in range(count):
                reward = random.choice(CHEST_REWARDS)
                if reward == 'scrap':
                    for i in range(15 + random.randint(0, int(self.parent.e['State'].wave * 0.4))):
                        self.parent.e['EntityGroups'].add(Drop('scrap', self.center), 'entities')
                if reward + '_b' in self.parent.e['Assets'].images['upgrades']:
                    self.parent.e['EntityGroups'].add(AbilityDrop(reward, self.center), 'entities')
                for i in range(self.parent.e['State'].upgrade_stat('investing')):
                    self.parent.e['EntityGroups'].add(Drop('scrap', self.center), 'entities')
                if random.random() < self.parent.e['State'].upgrade_stat('shield'):
                    self.parent.e['EntityGroups'].add(AbilityDrop('shield', self.center), 'entities')
                for i in range(random.randint(0, 3)):
                    self.parent.e['EntityGroups'].add(Drop('scrap', self.center), 'entities')
        elif self.type == 'stump':
            for i in range(random.randint(5, 7)):
                self.parent.e['EntityGroups'].add(Debris('plank', self.center), 'vfx')
        else:
            scrap_range = [0, random.choice([1, 1, 1, 1, 2])]
            if self.type == 'spawner':
                scrap_range = [1, 6]
            if src_weapon and (random.random() < src_weapon.enchant_stat('scrappy')):
                scrap_range[1] *= 2
            if self.parent.e['State'].score < 40:
                scrap_range[1] *= 2
                if self.parent.e['State'].effect_active('collector'):
                    scrap_range[1] *= 2
            elif self.parent.e['State'].effect_active('collector'):
                scrap_range[1] *= 3
            for i in range(random.randint(*scrap_range)):
                self.parent.e['EntityGroups'].add(Drop('scrap', self.center), 'entities')
            for i in range(random.randint(3, 5)):
                self.parent.e['EntityGroups'].add(Debris(random.choice(['machine_fragment', 'machine_fragment_2', 'machine_fragment_2']), self.center, force=0.35), 'vfx')

        for i in range(random.randint(5, 7)):
            anim = Animation('flash', (self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-9, 6)))
            anim.animation.update(random.random() * 0.6)
            anim.flip[0] = random.choice([True, False])
            self.parent.e['EntityGroups'].add(anim, 'vfx')

        if not silent:
            if self.parent.e['Settings'].screenshake:
                self.parent.e['Game'].camera.screenshake = max(self.parent.e['Game'].camera.screenshake, 0.15)

            self.parent.e['Game'].player.play_from('destroy', self.center, volume=0.7)

            if src_weapon and (random.random() < src_weapon.enchant_stat('hitrun')):
                self.parent.e['State'].add_effect('swiftness', 3)
                self.parent.e['Sounds'].play('powerup', volume=0.35)

            if self.type == 'beacon':
                self.parent.beacon = None
                anim = Animation('small_explosion', (self.center[0], self.center[1]))
                anim.flip[0] = random.choice([True, False])
                self.parent.e['EntityGroups'].add(anim, 'vfx')

            if self.parent.e['State'].effect_active('collateral'):
                for i in range(random.randint(3, 4)):
                    angle = random.random() * math.pi * 2
                    self.parent.e['EntityGroups'].add(Bullet('blue', self.center, angle, speed=110), 'entities')

            if self.type not in FRIENDLY_MACHINES:
                self.parent.e['State'].catalog_log('machines', self.type)
                total_destroys = self.parent.e['Steamworks'].increment_stat('kills', 1)
                if total_destroys >= 1000:
                    self.parent.e['Steamworks'].grant_achievement('hole_puncher')
                if total_destroys >= 10000:
                    self.parent.e['Steamworks'].grant_achievement('hole_puncher_ii')
                if total_destroys >= 100000:
                    self.parent.e['Steamworks'].grant_achievement('hole_puncher_iii')
                self.parent.e['State'].log_kill()

    def has_effect(self, effect_id):
        return self.effects.has_effect(effect_id)

    def apply_effect(self, effect_id, duration, src_weapon=None):
        if src_weapon and src_weapon.enchant_stat('splash'):
            for offset in OFFSET_N8:
                loc = (self.pos[0] + offset[0], self.pos[1] + offset[1])
                if loc in self.parent.machine_map:
                    if random.random() < src_weapon.enchant_stat('splash'):
                        self.parent.machine_map[loc].apply_effect(effect_id, duration)
        self.effects.apply_effect(effect_id, duration)

    def damage(self, damage, src_weapon=None, alternate_source=False):
        if not alternate_source:
            if self.health == self.max_health:
                damage *= (self.parent.e['State'].upgrade_stat('sledgehammer') + 1)
            if random.random() < self.parent.e['State'].upgrade_stat('flame'):
                self.apply_effect('flame', 4.2, src_weapon=src_weapon)
            elif self.parent.e['State'].effect_active('flame'):
                self.apply_effect('flame', 4.2, src_weapon=src_weapon)
            if random.random() < self.parent.e['State'].upgrade_stat('confusion'):
                if self.type not in FRIENDLY_MACHINES:
                    self.apply_effect('confusion', 3, src_weapon=src_weapon)
                    self.parent.e['Game'].player.play_from('confuse', self.center, volume=0.3)

        if src_weapon and (self.type == 'beacon'):
            damage *= (src_weapon.enchant_stat('fmj') + 1)

        if damage >= 50:
            self.parent.e['Steamworks'].grant_achievement('x50')
        
        old_health = self.health
        self.parent.e['Game'].player.process_damage_applied(self, damage)
        self.health = max(0, self.health - damage)
        self.hurt = 0.3
        for i in range(random.randint(1, 3)):
            anim = Animation('flash', (self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-9, 6)))
            anim.animation.update(random.random() * 0.3 + 0.3)
            anim.flip[0] = random.choice([True, False])
            self.parent.e['EntityGroups'].add(anim, 'vfx')
        self.parent.e['Game'].player.play_from('machine_hit', self.center, volume=0.7)
        if old_health and (not self.health):
            self.destroy(src_weapon=src_weapon)
            if random.random() < self.parent.e['State'].upgrade_stat('sludge'):
                self.parent.e['EntityGroups'].add(TempTerrain((1, 0), self.pos), 'entities')
        elif random.random() < (1 - 0.94 ** self.parent.e['State'].owned_upgrades['frost_touch']):
            self.apply_effect('freeze', 4, src_weapon=src_weapon)
            self.parent.e['Game'].player.play_from('freeze', self.center, volume=0.8)

    @property
    def center(self):
        tile_size = self.parent.e['Tilemap'].tile_size
        return ((self.pos[0] + 0.5) * tile_size, (self.pos[1] + 0.5) * tile_size)
    
    @property
    def inaccuracy(self):
        return 1 + self.parent.e['State'].upgrade_stat('smokescreen')
    
    @property
    def status_affected(self):
        return self.effects.status_affected
    
    def inaccuracy_offset(self, scale=0.12):
         return (self.inaccuracy - 1) * math.pi * scale * (random.random() - 0.5)

    def update(self, activate):
        self.hurt = max(0, self.hurt - self.parent.e['Window'].dt)
        self.alive_for += self.parent.e['Window'].dt
        self.size = [min(1, self.alive_for * 20), min(1, self.alive_for * 30)]

        if not self.effects.frozen:
            self.timer += self.parent.e['Window'].dt
        
        if activate and (not self.parent.e['State'].effect_active('freeze')):
            if self.parent.activation_index == (self.pos[0] + self.pos[1]) % self.parent.activation_groups:
                self.activate()
        
        if self.type in {'chest', 'spawner', 'beacon'}:
            self.parent.important_cells[tuple(self.pos)] = self

        if self.type in {'stump', 'chest'}:
            if len(self.parent.machine_map) < 64:
                if (not self.parent.e['HUD'].boss) or (not self.parent.e['HUD'].boss.health):
                    enemies_found = False
                    for machine in list(self.parent.machine_map.values()):
                        if machine.type not in {'stump', 'chest'}:
                            enemies_found = True
                    if self.parent.enemies_proper_remaining:
                        enemies_found = True
                    if not enemies_found:
                        self.destroy(silent=True)

        if (self.type == 'beacon') and (not self.effects.frozen):
            bullet_type = 'enemy_blue' if self.effects.confusion else 'red'
            if time.time() - self.parent.wave_start > 2:
                if self.timer > 0.25:
                    if time.time() % 10 < 6:
                        self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, (time.time() % math.pi) * 2), 'entities')
                        self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, (time.time() % math.pi) * 2 + math.pi), 'entities')
                    else:
                        for angle in [0, math.pi / 2, math.pi, math.pi * 3 / 2]:
                            self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, angle), 'entities')
                    self.timer -= 0.25
                    if self.timer > 0.25:
                        self.timer = 0.24
            else:
                self.timer = 0
        
        if self.parent.e['Settings'].aim_assist and (not self.ghosted):
            player = self.parent.e['Game'].player
            if pp.game_math.fast_range_check(player.center, self.center, player.weapon.max_range):
                angle = math.atan2(self.center[1] - player.center[1], self.center[0] - player.center[0])
                self.parent.machines_in_range.append((angle, len(self.parent.machines_in_range), self))

    def neighbor(self, offset):
        pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])
        if pos in self.parent.machine_map:
            return self.parent.machine_map[pos]
    
    def activate(self):
        bullet_type = 'enemy_blue' if self.effects.confusion else 'red'
        if (time.time() - self.parent.wave_start > 2) and (not self.effects.frozen):
            if self.type == 'cube':
                if not self.neighbor((1, 0)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, self.inaccuracy_offset()), 'entities')
                if not self.neighbor((-1, 0)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, math.pi + self.inaccuracy_offset()), 'entities')
                if not self.neighbor((0, 1)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, math.pi / 2 + self.inaccuracy_offset()), 'entities')
                if not self.neighbor((0, -1)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, -math.pi / 2 + self.inaccuracy_offset()), 'entities')
            elif self.type == 'bishop':
                if not self.neighbor((1, 1)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, math.pi / 4 + self.inaccuracy_offset()), 'entities')
                if not self.neighbor((-1, 1)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, math.pi * 3 / 4 + self.inaccuracy_offset()), 'entities')
                if not self.neighbor((-1, -1)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, math.pi * 5 / 4 + self.inaccuracy_offset()), 'entities')
                if not self.neighbor((1, -1)):
                    self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, math.pi * 7 / 4 + self.inaccuracy_offset()), 'entities')
            elif self.type == 'bouncer':
                bullet = Bullet(bullet_type, self.center, random.random() * math.pi * 2)
                bullet.bounces = 3
                self.parent.e['EntityGroups'].add(bullet, 'entities')
            elif self.type == 'volcano':
                if random.random() < 0.5:
                    offset = ((random.random() - 0.5) * 12 * 6, (random.random() - 0.5) * 12 * 6)
                    if not self.effects.confusion:
                        self.parent.e['EntityGroups'].add(Bomb(self.center, (self.parent.e['Game'].player.center[0] + offset[0] + self.inaccuracy * 20 * (random.random() - 0.5), self.parent.e['Game'].player.center[1] + offset[1] + self.inaccuracy * 20 * (random.random() - 0.5))), 'entities')
            elif self.type == 'crab':
                angle = math.atan2(self.parent.e['Game'].player.pos[1] - self.center[1], self.parent.e['Game'].player.pos[0] - self.center[0]) + (random.random() * 0.15 - 0.075) * self.inaccuracy
                self.parent.e['EntityGroups'].add(Bullet(bullet_type, self.center, angle), 'entities')
            elif self.type == 'sniper':
                if random.random() < 0.3:
                    angle = math.atan2(self.parent.e['Game'].player.pos[1] - self.center[1] + 5, self.parent.e['Game'].player.pos[0] - self.center[0]) + self.inaccuracy_offset(0.05)
                    if not self.effects.confusion:
                        self.parent.e['EntityGroups'].add(Laser((self.center[0], self.center[1] - 5), angle), 'entities')
            elif self.type == 'cylinder':
                if not self.effects.confusion:
                    self.parent.e['EntityGroups'].add(AttackCircle((self.center[0], self.center[1] - 5)), 'vfx')
                    for i in range(20):
                        self.parent.e['EntityGroups'].add(pp.vfx.Spark(self.center, random.random() * math.pi * 2, size=(random.randint(5, 7), 1), speed=random.random() * 120 + 120, decay=random.random() * 3 + 1, color=random.choice([(254, 252, 211), (38, 27, 46)]), z=0), 'vfx')

    def decay_render(self, offset):
        skip = False
        if self.pos in self.parent.machine_map:
            if (self.type not in STABLE_MACHINES) and (self.pos not in self.parent.last_machine_map):
                self.alive_for = 0
            else:
                skip = True
        if not skip:
            self.alive_for = min(1 / 15, self.alive_for)
            self.alive_for = max(0, self.alive_for - self.parent.e['Window'].dt)
        self.size = [min(1, self.alive_for * 15), min(1, self.alive_for * 22)]
        if not skip:
            self.render(offset)

    def render(self, offset):
        tile_size = self.parent.e['Tilemap'].tile_size
        rpos = [self.pos[0] * tile_size - offset[0] + MACHINE_OFFSETS[self.type][0], self.pos[1] * tile_size - offset[1] + MACHINE_OFFSETS[self.type][1]]
        if self.hurt:
            rpos[0] += random.randint(0, 4) - 2
            rpos[1] += random.randint(0, 4) - 2
        src_img = self.parent.e['Assets'].images['machines'][self.type]
        if self.ghosted:
            # don't show ghosted machines during machine events since they'll be removed by the shader
            if self.parent.high_life:
                return
            
            src_img = src_img.copy()
            src_img.set_alpha(100)

        if min(self.size) > 0:
            if not self.parent.high_life:
                marker = self.parent.e['VisibilityMarkers'].render_marker(self.pos, self.type, offset=MACHINE_OFFSETS[self.type], color=self.parent.e['State'].marker_color)
                if marker:
                    self.parent.e['Renderer'].blit(marker, rpos, z=9999)

            img = pygame.transform.scale(src_img, (src_img.get_width() * self.size[0], src_img.get_height() * self.size[1]))
            rpos[0] += (src_img.get_width() - img.get_width()) / 2
            rpos[1] += (src_img.get_height() - img.get_height()) / 2
            self.parent.e['Renderer'].blit(img, rpos, z=self.pos[1])

            if (not self.ghosted) and self.parent.e['Settings'].machine_outline and (self.type not in FRIENDLY_MACHINES):
                outline_img = self.parent.e['Assets'].images['machines'][self.type + '_outlined']
                outline_img = pygame.transform.scale(outline_img, ((outline_img.get_width() - 2) * self.size[0] + 2, (outline_img.get_height() - 2) * self.size[1] + 2))
                self.parent.e['Renderer'].blit(outline_img, (rpos[0] - 1, rpos[1] - 1), z=self.pos[1] - 0.0001)

        self.effects.update_render(offset=offset)

        if self.type == 'beacon':
            center = (rpos[0] + tile_size / 2, rpos[1] + tile_size / 2)
            for i, angle in enumerate([self.parent.e['Window'].time * 4, self.parent.e['Window'].time * 4 + math.pi / 4]):
                top = (center[0], center[1] - 50)
                triangles = [
                    [
                        pp.utils.game_math.advance(list(center), angle, 9),
                        top,
                        pp.utils.game_math.advance(list(center), angle + math.pi / 2, 9),
                    ],
                    [
                        pp.utils.game_math.advance(list(center), angle + math.pi / 2, 9),
                        top,
                        pp.utils.game_math.advance(list(center), angle + math.pi, 9),
                    ],
                    [
                        pp.utils.game_math.advance(list(center), angle + math.pi, 9),
                        top,
                        pp.utils.game_math.advance(list(center), angle + math.pi * 3 / 2, 9),
                    ],
                    [
                        pp.utils.game_math.advance(list(center), angle, 9),
                        top,
                        pp.utils.game_math.advance(list(center), angle + math.pi * 3 / 2, 9),
                    ],
                ]
                for triangle in triangles:
                    self.parent.e['Renderer'].renderf(pygame.draw.polygon, (38, 27, 46) if i == 0 else (254, 252, 211), triangle, width=1, group='default', z=self.pos[1] + 0.5)

class Machines(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.activation_groups = 16
        self.activation_rate = 1.5

        self.high_life_cooldown = 15
        self.high_life_duration = 18

        self.enemy_machine_cells_remaining = False

        self.wave_cleared = 0

        self.important_cells = {}

        self.patterns = {}
        for pattern in self.e['Assets'].images['patterns']:
            self.patterns[pattern] = []
            for rot in {0, 90, 180, 270}:
                self.patterns[pattern].append(pygame.transform.rotate(self.e['Assets'].images['patterns'][pattern], rot))

        Automata()
        
        self.reset(soft=True)

    @property
    def step_interval(self):
        return 0.1875 * self.e['State'].difficulty_set_stats['step_interval'] * self.e['State'].difficulty_status['step']

    @property
    def high_life(self):
        return max(0, self.high_life_timer)
    
    @property
    def high_life_time(self):
        return self.high_life_duration - self.high_life

    def reset(self, soft=False):
        self.active = False

        self.spawn_mask = None

        self.last_machine_map = {}
        self.machine_map = {}
        self.ghost_machine_map = {}

        self.no_enemy_dur = 0

        self.activation_index = 0
        self.activation_timer = 0

        self.steps_since_pause = 0
        self.pause = 0

        self.last_step = time.time()
        self.wave_start = time.time()

        self.beacon = None

        self.high_life_timer = -self.high_life_cooldown

        if not soft:
            self.new_wave()
        else:
            self.minimap = self.e['Tilemap'].minimap_base.copy()
            self.minimap.set_alpha(180)

        self.e['Automata'].update_dimensions(self.e['Tilemap'].dimensions)

        self.machines_in_range = []

    def spawn_wave(self, scale=1):
        wave_effect = self.e['State'].wave
        # jump back 20 waves in difficulty every loop
        wave_effect -= (max(0, wave_effect - 1) // 40) * 20
        difficulty = max(5, int((wave_effect * 1.6 + 4.857) * self.e['State'].difficulty_status['count'] * self.e['State'].difficulty_set_stats['machine_count'])) * scale
        tries = 0
        while difficulty > 0:
            choice = random.choice(list(SEASON_PATTERNS[self.e['State'].season]))
            if PATTERN_DIFFICULTY[choice] <= difficulty:
                difficulty -= PATTERN_DIFFICULTY[choice]
                if not self.place_spawn(choice):
                    difficulty += PATTERN_DIFFICULTY[choice]
                else:
                    tries = 0
            tries += 1
            if tries > 1000:
                break

    def new_wave(self, boss=False):
        self.active = True

        self.wave_cleared = 0

        self.e['Game'].player.damaged_in_wave = False

        if self.e['Game'].player.partner[0]:
            self.e['Game'].player.partner[0].health = self.e['Game'].player.partner[0].max_health

        self.e['Game'].player.height = 200

        self.e['State'].wave += 1

        self.e['State'].ending_shopping = False

        season = self.e['State'].season
        self.e['Music'].play(f'{season}_battle')

        self.e['State'].clear_map()

        if DEMO and (self.e['State'].wave > 10):
            self.e['Game'].restart()
            self.e['State'].popup = ['Thanks for playing the Yawnoc demo!', 200, self.e['Menus'].demo_win_callback, 0, ['Okay', 'Wishlist']]
            return

        if boss:
            load_successful = self.e['Tilemap'].load_boss_map()
        else:
            load_successful = self.e['Tilemap'].load_random_map()
        if not load_successful:
            return
        
        self.e['Automata'].update_dimensions(self.e['Tilemap'].dimensions)

        for frenemy_id in FRENEMY_LEVELS:
            # only spawn frenemies if the wave has never been beaten
            if (self.e['State'].wave == FRENEMY_LEVELS[frenemy_id]) and (self.e['State'].record < self.e['State'].wave):
                middle = (int(self.e['Tilemap'].dimensions[0] // 2) * self.e['Tilemap'].tile_size, int(self.e['Tilemap'].dimensions[1] // 2) * self.e['Tilemap'].tile_size)
                self.e['EntityGroups'].add(Frenemy(frenemy_id, middle), 'frenemies')

        player = self.e['Game'].player
        player.new_wave()
        player.pos = list(self.e['Tilemap'].spawn)
        if player.partner[0]:
            player.partner[0].pos = player.pos.copy()
            player.partner[0].height = player.height
            player.partner[0].weapon.reset()
        player.weapon.reset()
        if player.alt_weapon:
            player.alt_weapon.reset()

        self.minimap = self.e['Tilemap'].minimap_base.copy()
        self.minimap.set_alpha(180)

        self.high_life_timer = -10

        if not boss:
            self.e['State'].notify(f'Wave {self.e["State"].wave}')

        self.wave_start = time.time()
        self.pause = 5

        self.beacon = None
        wave_mod = self.e['State'].wave % 10
        if (wave_mod % 4 == 0) and wave_mod:
            # beacon wave
            middle = (int(self.e['Tilemap'].dimensions[0] // 2), int(self.e['Tilemap'].dimensions[1] // 2))
            self.machine_map[middle] = Machine(self, 'beacon', middle)
            self.beacon = self.machine_map[middle]

        self.generate_spawn_mask()

        if self.e['State'].wave < 3:
            if self.e['State'].wave < 2:
                spawn_list = ['beacon', 'blinker']
            else:
                spawn_list = ['glider', 'glider', 'beacon', 'tub']
            while len(spawn_list):
                if self.place_spawn(spawn_list[0]):
                    spawn_list.pop(0)
        elif not boss:
            self.spawn_wave(scale=1)
        else:
            self.e['EntityGroups'].add(Eye((self.e['Tilemap'].dimensions[0] / 2 * self.e['Tilemap'].tile_size, self.e['Tilemap'].dimensions[1] / 2 * self.e['Tilemap'].tile_size)), 'frenemies')

        for i in range(min(self.e['State'].wave, random.randint(2, 3)) + int(self.e['State'].upgrade_stat('treasure_trove'))):
            self.place_spawn('chest', machine_type='chest')
        
        area = self.e['Tilemap'].dimensions[0] * self.e['Tilemap'].dimensions[1]
        if self.e['State'].season != 'void':
            stump_count = int(area / 500 * (random.random() + 0.2))
            for i in range(stump_count):
                self.place_spawn('chest', machine_type='stump')

    def end_wave(self):
        self.e['Steamworks'].store_stats()
        self.active = False
        self.ghost_machine_map = {}
        if (self.e['State'].wave - 1) % 40 == 39:
            self.e['State'].popup = ['The eye is near.\nChallenge it?', 200, self.e['State'].challenge_callback, 0, ['Loop', 'Challenge']]
        else:
            self.e['State'].shop()

    def generate_spawn_mask(self):
        spawn_surf = self.minimap.copy()
        for machine in self.machine_map.values():
            spawn_surf.set_at(machine.pos, (255, 255, 255))
        pygame.draw.rect(spawn_surf, (255, 255, 255), pygame.Rect(self.e['Game'].player.center[0] // self.e['Tilemap'].tile_size - 2, self.e['Game'].player.center[1] // self.e['Tilemap'].tile_size - 2, 5, 5))
        spawn_surf.set_colorkey((0, 0, 0))
        self.spawn_mask = pygame.mask.from_surface(spawn_surf)

    def midwave_spawn(self, pattern, machine_type=None):
        self.generate_spawn_mask()
        self.place_spawn(pattern, machine_type=machine_type)

    def place_spawn(self, pattern, machine_type=None):
        pattern = random.choice(self.patterns[pattern])
        pattern_mask = pygame.mask.Mask(pattern.get_size(), fill=True)
        for i in range(50):
            spawn = (random.randint(3, self.e['Tilemap'].dimensions[0] - 3 - pattern.get_width()), random.randint(3, self.e['Tilemap'].dimensions[1] - 3 - pattern.get_height()))
            if not self.spawn_mask.overlap(pattern_mask, spawn):
                self.spawn_mask.draw(pattern_mask, spawn)
                if self.spawn(pattern, spawn, machine_type=machine_type):
                    return True

    def machine_by_px(self, pos_px):
        tile_size = self.e['Tilemap'].tile_size
        loc = (int(pos_px[0] // tile_size), int(pos_px[1] // tile_size))
        if loc in self.machine_map:
            return self.machine_map[loc]

    def spawn(self, pattern, pos, machine_type=None):
        if not machine_type:
            # fall just starts with spawners
            if self.e['State'].season == 'fall':
                machine_type = 'spawner'
            else:
                machine_types = WEIGHTED_MACHINE_TYPES[:10]
                if self.e['State'].wave < 2:
                    machine_types = WEIGHTED_MACHINE_TYPES[:2]
                elif self.e['State'].wave < 3:
                    machine_types = WEIGHTED_MACHINE_TYPES[:3]
                elif self.e['State'].wave < 4:
                    machine_types = WEIGHTED_MACHINE_TYPES[:4]
                elif self.e['State'].wave < 11:
                    machine_types = WEIGHTED_MACHINE_TYPES[:6]
                elif self.e['State'].wave < 21:
                    machine_types = WEIGHTED_MACHINE_TYPES[:8]
                machine_type = random.choice(machine_types)
        if type(pattern) != pygame.Surface:
            pattern = random.choice(self.patterns[pattern])

        # check to avoid spawning in walls
        valid = True
        for y in range(pattern.get_height()):
            for x in range(pattern.get_width()):
                lookup_pos = (x, y)
                if pattern.get_at(lookup_pos)[:3] == (255, 255, 255):
                    spawn_pos = (x + pos[0], y + pos[1])
                    if (spawn_pos in self.e['Tilemap'].solids) or (spawn_pos in self.e['Tilemap'].gaps):
                        valid = False
                        break
            if not valid:
                break
        
        if valid:
            for y in range(pattern.get_height()):
                for x in range(pattern.get_width()):
                    lookup_pos = (x, y)
                    if pattern.get_at(lookup_pos)[:3] == (255, 255, 255):
                        spawn_pos = (x + pos[0], y + pos[1])
                        if spawn_pos not in self.machine_map:
                            self.machine_map[spawn_pos] = Machine(self, machine_type, spawn_pos)
            return True

    def step(self, activate_cycle=False):
        if len(self.machine_map):
            self.e['Sounds'].play('tick', volume=0.12)

            if self.e['State'].season == 'fall':
                self.e['Automata'].current_automata = 'brain'
                if self.high_life:
                    self.e['State'].catalog_log('automata', 'migraine')
                else:
                    self.e['State'].catalog_log('automata', 'brain')
            elif self.e['State'].season == 'winter':
                if self.high_life:
                    self.e['Automata'].current_automata = 'blursed'
                    self.e['State'].catalog_log('automata', 'blursed')
                else:
                    self.e['Automata'].current_automata = 'blobell'
                    self.e['State'].catalog_log('automata', 'blobell')
            elif self.e['State'].season == 'void':
                self.e['Automata'].current_automata = 'lowdeath'
                self.e['State'].catalog_log('automata', 'lowdeath')
            else:
                if self.high_life:
                    self.e['Automata'].current_automata = 'highlife'
                    self.e['State'].catalog_log('automata', 'highlife')
                else:
                    self.e['Automata'].current_automata = 'cgol'
                    self.e['State'].catalog_log('automata', 'cgol')

            self.e['Automata'].clear()
            automata_surf = self.e['Automata'].automata_map
            for loc in self.machine_map:
                automata_surf.set_at(loc, (MACHINE_ID[self.machine_map[loc].type], self.machine_map[loc].green_stat, 0, 255))
            for loc in self.ghost_machine_map:
                automata_surf.set_at(loc, (MACHINE_ID[self.ghost_machine_map[loc].type], self.ghost_machine_map[loc].green_stat, 0, 255))
            
            self.e['Automata'].step()

            self.minimap = self.e['Tilemap'].minimap_base.copy()

            old_machine_map = self.machine_map.copy()
            old_ghost_machine_map = self.ghost_machine_map.copy()
            self.machine_map = {}
            self.ghost_machine_map = {}
            activate_list = []

            automata_surf = self.e['Automata'].automata_map

            for y in range(automata_surf.get_height()):
                for x in range(automata_surf.get_width()):
                    loc = (x, y)
                    src_color = automata_surf.get_at(loc)
                    if src_color[0] > 0:
                        if (loc not in self.e['Tilemap'].solids) and (loc not in self.e['Tilemap'].gaps):
                            green_stat = src_color[1]
                            if (green_stat == 255) or (self.e['State'].season != 'fall'):
                                if loc in old_machine_map:
                                    self.machine_map[loc] = old_machine_map[loc]
                                    self.machine_map[loc].green_stat = green_stat
                                else:
                                    self.machine_map[loc] = Machine(self, INV_MACHINE_ID[src_color[0]], loc, green=green_stat)
                                    activate_list.append(loc)
                                if INV_MACHINE_ID[src_color[0]] in STABLE_MACHINES:
                                    if INV_MACHINE_ID[src_color[0]] == 'stump':
                                        self.minimap.set_at(loc, (100, 97, 139))
                                    elif INV_MACHINE_ID[src_color[0]] == 'chest':
                                        self.minimap.set_at(loc, (228, 103, 71))
                                    else:
                                        self.minimap.set_at(loc, (125, 43, 88))
                                else:
                                    self.minimap.set_at(loc, (254, 252, 211))
                            else:
                                if loc in old_ghost_machine_map:
                                    self.ghost_machine_map[loc] = old_ghost_machine_map[loc]
                                    self.ghost_machine_map[loc].green_stat = green_stat
                                else:
                                    self.ghost_machine_map[loc] = Machine(self, INV_MACHINE_ID[src_color[0]], loc, green=green_stat, ghosted=True)
                                self.minimap.set_at(loc, (100, 97, 139))

            if activate_cycle:
                for loc in activate_list:
                    if random.random() < 0.5:
                        self.machine_map[loc].activate()
            
            self.last_machine_map = old_machine_map

            self.minimap.set_alpha(180)

    def recompute_remaining_cells(self):
        self.enemy_machine_cells_remaining = False
        for machine in self.machine_map.values():
            if machine.type not in FRIENDLY_MACHINES:
                self.enemy_machine_cells_remaining = True

    @property
    def enemies_proper_remaining(self):
        return ('enemies' in self.e['EntityGroups'].groups) and len(self.e['EntityGroups'].groups['enemies'])

    @property
    def active_enemies_remaining(self):
        if self.enemy_machine_cells_remaining:
            return True
        if ('enemies' in self.e['EntityGroups'].groups) and len(self.e['EntityGroups'].groups['enemies']):
            return True
        if ('frenemies' in self.e['EntityGroups'].groups) and len([f for f in self.e['EntityGroups'].groups['frenemies'] if (not f.friendly) and f.health]):
            return True
        if (self.e['HUD'].boss and (self.e['HUD'].boss.type == 'eye')):
            return True
        return False
    
    @property
    def non_boss_enemies_remaining(self):
        if self.enemy_machine_cells_remaining:
            return True
        if ('enemies' in self.e['EntityGroups'].groups) and len(self.e['EntityGroups'].groups['enemies']):
            return True
        if ('frenemies' in self.e['EntityGroups'].groups) and len([f for f in self.e['EntityGroups'].groups['frenemies'] if ((not f.friendly) and (f.type[:3] != 'eye'))]):
            return True
        return False

    @property
    def enemies_remaining(self):
        if self.e['HUD'].boss:
            return True
        return self.non_boss_enemies_remaining
    
    def paused_update(self):
        self.last_step += self.e['Window'].dt
        self.wave_start += self.e['Window'].dt

    def update(self):
        self.important_cells = {}

        if (not self.e['State'].title) and self.active and (not self.e['State'].ui_busy):
            if not self.enemies_remaining:
                if not self.e['State'].shopping:
                    self.no_enemy_dur += self.e['Window'].dt
                    if self.no_enemy_dur > 4:
                        self.end_wave()
                        self.last_machine_map = self.machine_map
                        self.no_enemy_dur = 0
            else:
                self.no_enemy_dur = 0

        self.recompute_remaining_cells()

        if (not (self.active_enemies_remaining or self.wave_cleared)) and self.active and (not self.e['State'].ui_busy):
            self.e['Game'].freeze_stack.append([0.1, 1])
            self.wave_cleared = 1
        
        if (self.wave_cleared == 1) and (not len(self.e['Game'].freeze_stack)):
            self.wave_cleared = 2
            self.e['Sounds'].play('complete', volume=1.0)
            self.e['State'].notify('Wave Complete')
            self.e['State'].clear_effect('miasma')

        if not self.e['Game'].player.moved:
            self.last_step = time.time()
            self.wave_start = time.time()

        if (time.time() - self.wave_start > 210) and self.active_enemies_remaining and (not self.wave_cleared):
            if (not self.e['HUD'].boss) or (self.e['HUD'].boss.type[:3] != 'eye'):
                if not self.e['State'].effect_active('miasma'):
                    self.e['State'].notify(f'Machine Event: Miasma')
                    self.e['State'].add_effect('miasma', 10000, hidden=True)
                    self.e['Sounds'].play('cough', volume=0.65)
                    self.e['Game'].player.miasma_cooldown = 5

        self.high_life_timer -= self.e['Window'].dt
        if (self.high_life_timer + self.e['Window'].dt >= 0) and (self.high_life_timer < 0):
            self.e['Sounds'].play('highlife_transition', volume=0.5)
            self.e['State'].notify('Machines Returned to Normal')
            self.e['HUD'].flash = 1
            self.e['Sounds'].sounds['ambience'].set_volume(self.e['Settings'].sfx_volume * 0.6)
            season = self.e['State'].season
            self.e['Music'].play(f'{season}_battle', start=self.e['Window'].time, fadein=1.0)

        if (self.high_life_timer > 0) and (self.high_life_timer < 0.5):
            self.e['Music'].fadeout(0.5)

        if (not self.pause) and (not self.e['State'].effect_active('freeze')) and (not (self.e['Transition'].progress or self.e['Transition'].level_end)) and (not self.e['State'].title):
            if time.time() - self.last_step > self.step_interval:
                self.step(self.steps_since_pause % max(4, math.ceil(8 - self.e['State'].difficulty / 50)) == 0)
                self.last_step = time.time()
                if self.steps_since_pause == 0:
                    if self.beacon and (self.high_life_timer <= -self.high_life_cooldown) and (random.random() < 0.2) and (self.e['State'].season != 'void'):
                        self.high_life_timer = self.high_life_duration
                        self.e['Sounds'].play('highlife_transition', volume=0.5)
                        self.e['State'].notify(f'Machine Event: {EVENT_NAMES[self.e["State"].season]}')
                        self.e['HUD'].flash = 1
                        self.e['Sounds'].sounds['ambience'].set_volume(0.02)
                        self.e['Music'].play('highlife')

                difficulty = self.e['State'].wave * 3 + 4
                if self.beacon and (len(self.machine_map) < difficulty * 3) and (random.random() < 0.1):
                    self.midwave_spawn(random.choice(MINOR_PATTERNS[self.e['State'].season]))

                if (len(self.machine_map) > 45) and (random.random() < 0.02):
                    self.midwave_spawn('chest', machine_type='chest')

                bb_activate_interval = 3 if self.high_life else 7
                if (not (self.steps_since_pause % bb_activate_interval)) and (self.e['State'].season == 'fall'):
                    # let spawners spawn any of the first 6 machine types
                    self.e['Automata'].uniforms['spawner_spawn_id'] = random.randint(100, 105)
                else:
                    self.e['Automata'].uniforms['spawner_spawn_id'] = 0

                self.steps_since_pause += 1
                if self.steps_since_pause >= 16:
                    self.steps_since_pause = 0
                    self.pause = self.e['State'].difficulty_status['pause'] * self.e['State'].difficulty_set_stats['step_pause']
        else:
            self.pause = max(0, self.pause - self.e['Window'].dt)

        activate = False
        self.activation_timer += self.e['Window'].dt
        while self.activation_timer > 1 / self.activation_rate:
            self.activation_timer -= 1 / self.activation_rate
            self.activation_index = (self.activation_index + 1) % self.activation_groups
            activate = True

        for machine in list(self.machine_map.values()):
            machine.update(activate)
        for machine in list(self.ghost_machine_map.values()):
            machine.update(False)

    def render(self):
        for machine in list(self.machine_map.values()):
            machine.render(self.e['Game'].camera)
        for machine in self.ghost_machine_map.values():
            machine.render(self.e['Game'].camera)

        if time.time() - self.last_step < 1 / 15:
            for machine in self.last_machine_map.values():
                machine.decay_render(self.e['Game'].camera)

TYPES.Machine = Machine