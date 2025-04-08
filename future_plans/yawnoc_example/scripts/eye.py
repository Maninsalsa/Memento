import math
import time
import random

import pygame

from . import pygpen as pp

from .animation import Animation
from .bullet import Bullet
from .laser import Laser
from .effects import EntityEffects
from .const import Difficulties, TYPES

class Eye(pp.ElementSingleton):
    def __init__(self, pos, scale=1.0, parent=None, local_id=0):
        super().__init__()

        self.pos = list(pos)
        self.scale = scale
        self.type = 'eye'
        if scale < 1:
            self.type = 'eye_small'
        self.friendly = False

        self.health = 420
        if scale < 1:
            self.health = 30
        self.health *= self.e['State'].difficulty_set_stats['enemy_health']
        self.max_health = self.health

        self.effects = EntityEffects(self)
        self.effects.z_offset = 1.1

        self.blink_cooldown = 0
        self.hurt = 0

        self.squinting = False

        self.kb_stack = []

        self.last_attack = random.random() * 0.15 - 5
        self.attack_phase = [0, random.random() * 8 + 2]
        self.parent = parent
        self.children = []
        self.timer = 0
        self.local_id = local_id
        self.last_hit_child = None

    @property
    def radius(self):
        return self.scale * 19
    
    @property
    def hitbox_radius(self):
        return self.radius * 0.6
    
    @property
    def center(self):
        return self.pos
    
    @property
    def boss(self):
        return self.scale >= 1
    
    def has_effect(self, effect_id):
        return self.effects.has_effect(effect_id)

    def apply_effect(self, effect_id, duration, src_weapon=None):
        self.effects.apply_effect(effect_id, duration)

    @property
    def status_affected(self):
        return self.effects.status_affected
    
    def damage(self, damage, src_weapon=None, alternate_source=False):
        if self.health == self.max_health:
            damage *= (self.e['State'].upgrade_stat('sledgehammer') + 1)

        if not alternate_source:
            if random.random() < self.e['State'].upgrade_stat('flame'):
                self.apply_effect('flame', 4.2, src_weapon=src_weapon)
            elif self.e['State'].effect_active('flame'):
                self.apply_effect('flame', 4.2, src_weapon=src_weapon)

        if src_weapon:
            damage *= (src_weapon.enchant_stat('fmj') + 1)

        if damage >= 50:
            self.e['Steamworks'].grant_achievement('x50')

        self.e['Game'].player.process_damage_applied(self, damage)

        if (not self.squinting) and damage:
            if self.boss:
                if self.health < 0.34 * self.max_health:
                    damage *= 0.5
                if (self.health > 0.67 * self.max_health) and (self.health - damage) <= 0.67 * self.max_health:
                    self.e['Machines'].spawn_wave(scale=0.6)
                    self.e['Machines'].wave_start = time.time()
                    self.e['Sounds'].play('glass_shatter', volume=1.0)
                    self.squinting = True
                    self.e['HUD'].flash = 1
                if (self.health > 0.34 * self.max_health) and (self.health - damage) <= 0.34 * self.max_health:
                    self.e['Machines'].spawn_wave(scale=0.6)
                    self.e['Machines'].wave_start = time.time()
                    self.e['Sounds'].play('glass_shatter', volume=1.0)
                    self.squinting = True
                    self.e['HUD'].flash = 1
                    for i in range(8):
                        eye = Eye(pp.game_math.advance(list(self.pos), i / 8 * math.pi * 2, 90), scale=0.5, parent=self, local_id=i)
                        self.e['EntityGroups'].add(eye, 'frenemies')
                        self.children.append(eye)
            if self.parent:
                self.parent.last_hit_child = self
            self.health = max(0, self.health - damage)
            self.hurt = 0.3
            self.blink_cooldown = -0.2
            for i in range(random.randint(1, 3)):
                anim = Animation('flash', (self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-9, 6)))
                anim.animation.update(random.random() * 0.3 + 0.3)
                anim.flip[0] = random.choice([True, False])
                self.e['EntityGroups'].add(anim, 'vfx')
            self.e['Game'].player.play_from('machine_hit', self.center, volume=0.7)
        else:
            self.e['Game'].player.play_from('ricochet', self.center, volume=0.7)
        return True
    
    def destroy(self):
        self.e['Game'].freeze_stack.append([0.1, 1])
        for i in range(20):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.center, random.random() * math.pi * 2, size=(random.randint(5, 7), 1), speed=random.random() * 120 + 120, decay=random.random() * 4 + 2, color=random.choice([(254, 252, 211), (38, 27, 46)]), z=0), 'vfx')
        for i in range(random.randint(5, 7)):
            anim = Animation('flash', (self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-9, 6)))
            anim.animation.update(random.random() * 0.6)
            anim.flip[0] = random.choice([True, False])
            self.e['EntityGroups'].add(anim, 'vfx')
        if self.e['Settings'].screenshake:
            self.e['Game'].camera.screenshake = max(self.e['Game'].camera.screenshake, 0.15)

        self.e['Game'].player.play_from('destroy', self.center, volume=1.0)

        anim = Animation('small_explosion', (self.center[0], self.center[1]))
        anim.flip[0] = random.choice([True, False])
        self.e['EntityGroups'].add(anim, 'vfx')

        if self.parent:
            if self in self.parent.children:
                self.parent.children.remove(self)

        if self.boss:
            self.e['Sounds'].play('glass_shatter', volume=1.0)
            self.e['State'].catalog_log('machines', 'eye')
            self.e['State'].clear_map()
            self.e['PauseMenu'].pause(mode='victory')
            self.e['Transition'].transition_timer = 1
            self.e['Transition'].callback = None
            self.e['Transition'].direction = 1
            self.e['HUD'].flash = 1
            self.e['Sounds'].play('glass_shatter', volume=1.0)
            self.e['Music'].fadeout(0.5)
            self.e['State'].catalog_log('machines', 'eye')
            if self.e['State'].difficulty_set == Difficulties.EXTRAHARD:
                self.e['Steamworks'].grant_achievement('victory_iii')
            elif self.e['State'].difficulty_set == Difficulties.HARD:
                self.e['Steamworks'].grant_achievement('victory_ii')
            self.e['Steamworks'].grant_achievement('victory')
            if not self.e['Game'].player.damaged_in_wave:
                self.e['Steamworks'].grant_achievement('not_a_scratch')
            self.e['Steamworks'].store_stats()

    def update(self, dt):
        self.kb_stack = []

        self.blink_cooldown -= dt
        if self.blink_cooldown < -0.5:
            self.blink_cooldown = random.random() * 3 + 2

        self.last_attack += dt
        self.timer += dt

        self.hurt = max(0, self.hurt - dt)

        if self.boss:
            self.e['HUD'].boss = self
            if self.health <= 0.34 * self.max_health:
                self.e['Game'].crack_img = self.e['Game'].cracks[2]
            elif self.health <= 0.67 * self.max_health:
                self.e['Game'].crack_img = self.e['Game'].cracks[1]
            if self.last_hit_child and self.last_hit_child.health:
                self.e['HUD'].boss = self.last_hit_child
            if self.squinting:
                if (not self.e['Machines'].non_boss_enemies_remaining) and (not len(self.children)):
                    self.squinting = False
                    self.attack_phase = [0, 8]
            elif (time.time() - self.e['Machines'].wave_start > 2):
                self.attack_phase[1] -= dt
                if self.attack_phase[1] < 0:
                    if self.health > 0.67 * self.max_health:
                        self.attack_phase[0] = (self.attack_phase[0] + 1) % 3
                    else:
                        self.attack_phase[0] = (self.attack_phase[0] + 1) % 5
                    if self.attack_phase[0] != 2:
                        self.attack_phase[1] += 8.5
                        if self.attack_phase[0] == 1:
                            self.last_attack = -2
                    else:
                        self.attack_phase[1] += 3.5
                
                if self.attack_phase[0] == 0:
                    if self.last_attack > 0.06:
                        self.e['EntityGroups'].add(Bullet('red', self.center, ((time.time() * 2) % math.pi) * 2 + math.pi), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, ((time.time() * 2) % math.pi) * 2), 'entities')
                        self.last_attack = 0
                        self.e['Game'].player.play_from('shoot', self.center, volume=0.2)
                if self.attack_phase[0] == 1:
                    if self.last_attack > 1.2:
                        angle = math.atan2(self.e['Game'].player.center[1] - self.center[1], self.e['Game'].player.center[0] - self.center[0])
                        for i in range(30):
                            bullet = Bullet('red', self.center, angle + (random.random() * 2 - 1) * 0.3)
                            bullet.speed = 250 + random.random() * 100
                            self.e['EntityGroups'].add(bullet, 'entities')
                        self.last_attack = 0
                        self.e['Game'].player.play_from('shotgun_shoot', self.center, volume=0.3)
                if self.attack_phase[0] == 3:
                    if self.last_attack > 2:
                        self.last_attack = 0
                        for i in range(40):
                            angle = i / 40 * math.pi * 2
                            self.e['EntityGroups'].add(Bullet('red', self.center, angle), 'entities')
                            if i % 5 == 0:
                                self.e['EntityGroups'].add(Laser(self.center, angle + time.time(), no_dot=True, rot_vel=0.15), 'entities')
                        self.e['Game'].player.play_from('boom', self.center, volume=0.3)
                if self.attack_phase[0] == 4:
                    if self.last_attack > 0.04:
                        angle = random.random() * math.pi * 2
                        bullet = Bullet('red', self.center, angle)
                        bullet.bounces = 3
                        self.e['EntityGroups'].add(bullet, 'entities')
                        self.e['Game'].player.play_from('shoot', self.center, volume=0.2)
                        self.last_attack = 0
        else:
            angle = math.atan2(self.pos[1] - self.parent.pos[1], self.pos[0] - self.parent.pos[0])
            self.pos = pp.game_math.advance(list(self.parent.pos), angle + dt * 0.25, math.cos(time.time() * 4.5) * 10 + 90)
            if self.parent.children.index(self) in {0, 4}:
                if self.last_attack > 0.2:
                    if self.local_id % 4 == 0:
                        self.e['EntityGroups'].add(Bullet('red', self.center, angle), 'entities')
                    if self.local_id % 4 == 1:
                        self.e['EntityGroups'].add(Bullet('red', self.center, 0), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi / 2), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi * 3 / 2), 'entities')
                    if self.local_id % 4 == 2:
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi / 4), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi * 3 / 4), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi * 5 / 4), 'entities')
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.pi * 7 / 4), 'entities')
                    if self.local_id % 4 == 3:
                        self.e['EntityGroups'].add(Bullet('red', self.center, math.atan2(self.e['Game'].player.pos[1] - self.pos[1], self.e['Game'].player.pos[0] - self.pos[0])), 'entities')
                    self.last_attack = 0
                    self.e['Game'].player.play_from('shoot', self.center, volume=0.1)
                self.squinting = False
            else:
                self.squinting = True

        if (not self.squinting) and (self.blink_cooldown > 0):
            if random.random() < dt * self.scale * 100:
                self.e['EntityGroups'].add(pp.vfx.Spark((self.pos[0] + (random.random() * 2 - 1) * self.radius, self.pos[1] + random.random() * self.radius * 0.5), (random.random() * 2 - 1) * math.pi / 4 + math.pi / 2, size=(random.randint(3, 5), 1), speed=random.random() * 60 + 30, decay=random.random() * 2 + 1, color=random.choice([(191, 60, 96), (252, 252, 211)]), z=0), 'vfx')
        
        self.effects.update()

        if not self.health:
            self.destroy()
            return True

    def renderz(self, offset=(0, 0), group='default'):
        self.effects.render()

        angle = math.atan2(self.e['Game'].player.center[1] - self.pos[1], self.e['Game'].player.center[0] - self.pos[0])
        dis = pp.game_math.distance(self.pos, self.e['Game'].player.center)
        eye_pull = min(1, dis / 200)

        openness = 1
        if self.blink_cooldown < 0:
            openness = min(1, max(0, -self.blink_cooldown * 2.25 - 0.2))
        if self.squinting:
            openness = 0.25
        pupil_scale = min(1, (self.last_attack * 3 if self.last_attack >= 0 else 1) + 0.5)
        points = [
            [-self.radius, -self.radius * 0.25 * openness],
            [-self.radius * 0.6, -self.radius * 0.5 * openness],
            [self.radius * 0.6, -self.radius * 0.5 * openness],
            [self.radius, -self.radius * 0.25 * openness],
            [self.radius, self.radius * 0.25 * openness],
            [self.radius * 0.6, self.radius * 0.5 * openness],
            [-self.radius * 0.6, self.radius * 0.5 * openness],
            [-self.radius, self.radius * 0.25 * openness],
        ]
        points = [(p[0] + self.radius, p[1] + self.radius) for p in points]

        pupil_points = [
            [-self.radius * 0.3 * pupil_scale, -self.radius * 0.25 * pupil_scale],
            [-self.radius * 0.2 * pupil_scale, -self.radius * 0.5 * pupil_scale],
            [self.radius * 0.2 * pupil_scale, -self.radius * 0.5 * pupil_scale],
            [self.radius * 0.3 * pupil_scale, -self.radius * 0.25 * pupil_scale],
            [self.radius * 0.3 * pupil_scale, self.radius * 0.25 * pupil_scale],
            [self.radius * 0.2 * pupil_scale, self.radius * 0.5 * pupil_scale],
            [-self.radius * 0.2 * pupil_scale, self.radius * 0.5 * pupil_scale],
            [-self.radius * 0.3 * pupil_scale, self.radius * 0.25 * pupil_scale],
        ]
        pupil_points = [(p[0] + self.radius + math.cos(angle) * eye_pull * self.radius * self.scale * 0.7, p[1] + self.radius + math.sin(angle) * eye_pull * self.radius * self.scale * 0.5) for p in pupil_points]

        if openness:
            base_surf = pygame.Surface((self.radius * 2, self.radius * 2))
            pygame.draw.polygon(base_surf, (254, 252, 211), points)
            mask = base_surf.copy()
            mask.set_colorkey((254, 252, 211))

            if self.hurt:
                offset = (offset[0] + random.random() * 4 - 2, offset[1] + random.random() * 4 - 2)

            if self.scale >= 1:
                red_wave = pygame.Surface((self.radius * 2, self.radius * 2))
                red_wave.blit(self.e['Assets'].images['misc']['red_wave'], (0, (-self.e['Window'].time % 2) * self.radius * 2.5 - 8))
                circuit_mask = self.e['Assets'].images['misc']['circuit_mask']
                circuit_mask.set_colorkey((255, 255, 255))
                red_wave.blit(circuit_mask, (0, 0))
                red_wave.set_colorkey((0, 0, 0))
                base_surf.blit(red_wave, (0, 0))

            pygame.draw.polygon(base_surf, (191, 60, 96), pupil_points, width=3)
            pygame.draw.polygon(base_surf, (30, 30, 50), pupil_points)
            base_surf.blit(mask, (0, 0))
            base_surf.set_colorkey((0, 0, 0))

            self.e['Renderer'].blit(base_surf, (self.pos[0] - offset[0] - self.radius, self.pos[1] - offset[1] - self.radius), z=self.pos[1] / self.e['Tilemap'].tile_size + 1.5, group=group)

TYPES.Eye = Eye