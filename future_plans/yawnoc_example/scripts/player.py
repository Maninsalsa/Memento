import math
import random

import pygame

from . import pygpen as pp

from .physics_entity import PhysicsEntity
from .animation import Animation
from .weapon import Weapon
from .bullet import Bullet, aoe_friendly_attack_range
from .const import TYPES, ABILITY_DURATIONS

class Player(PhysicsEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base_speed = 70

        self.weapon = Weapon('rifle', self)
        self.alt_weapon = None
        self.swap_cooldown = 0

        self.angle = 0

        self.roll_cooldown = 0
        self.roll_direction = 0
        self.roll_angle = 0

        self.kb_stack = []
        self.roll_damaged = set()
        self.guard_stacks = []
        self.stored_powerups = []

        self.last_movement = (1, 0)

        self.v_velocity = 0
        self.gravity = -300
        self.height = 0

        self.hurt = 0
        self.iframes = 0
        self.invisible = 0
        self.max_health = 5.2
        self.health = self.max_health
        self.shield = 0

        self.hitbox = pygame.Rect(self.pos[0], self.pos[1] - 8, 9, 14)

        self.moved = False

        self.last_movement_flip = False

        self.friendly = True

        self.partner = [None, 0]

        self.deathspiral_cooldown = 0

        self.miasma_cooldown = 10

        # a hack for dealing damage
        self.local_bullet = None

        self.shop_landed = False

        self.name = ''

        self.damaged_in_wave = False
    
    @property
    def swap_cooldown_amt(self):
        return 0.5 * (1 - self.e['State'].upgrade_stat('fast_hands'))
    
    @property
    def roll_cooldown_amt(self):
        return 1 * (1 - self.e['State'].upgrade_stat('rolypoly'))

    @property
    def speed(self):
        return self.base_speed * (1.06 ** self.e['State'].owned_upgrades['swiftness']) * (2 if self.e['State'].effect_active('swiftness') else 1)

    @property
    def dead(self):
        return not self.health

    @property
    def rolling(self):
        return self.roll_direction != 0
    
    @property
    def grid_pos(self):
        return (self.rect.center[0] // self.e['Tilemap'].tile_size, self.rect.center[1] // self.e['Tilemap'].tile_size)
    
    def reset(self):
        self.max_health = 5.2
        self.health = self.max_health
        self.shield = 0
        self.alt_weapon = None
        self.stored_powerups = []

    def new_wave(self):
        self.shield = self.e['State'].upgrade_stat('guards_buckle')
        self.stored_powerups = []

    def attack_hook(self):
        play_sound = False
        for powerup in self.stored_powerups:
            self.e['State'].add_effect(powerup, ABILITY_DURATIONS[powerup])
            if powerup != 'shield':
                play_sound = True
        if play_sound:
            self.e['Sounds'].play('powerup', volume=0.45)
        self.stored_powerups = []
    
    def heal(self, amt):
        self.health = min(self.max_health, self.health + amt)
        if self.partner[0]:
            self.partner[0].heal(amt * self.e['State'].upgrade_stat('leftovers'))

    def guard(self, amt, duration):
        self.e['Sounds'].play('shield_applied', volume=1.0)
        self.guard_stacks.append([duration, duration, amt])
        self.guard_stacks.sort()

    @property
    def total_shield(self):
        return self.shield + sum([stack[2] for stack in self.guard_stacks])
    
    def process_damage_applied(self, target, amt):
        if self.e['State'].effect_active('lifesteal'):
            self.heal(amt * 0.03)
    
    def die(self):
        self.e['Transition'].transition()
        for i in range(50):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.center, random.random() * math.pi * 2, size=(random.randint(5, 12), random.randint(1, 2)), speed=random.random() * 60 + 60, decay=random.random() * 2 + 0.5, color=random.choice([(254, 252, 211), (191, 60, 96)]), z=0), 'vfx')

    def play_from(self, sound, pos, volume=1.0):
        center = [self.e['Game'].camera.pos[0] + self.e['Game'].camera.size[0] / 2, self.e['Game'].camera.pos[1] + self.e['Game'].camera.size[1] / 2]
        angle = math.degrees(math.atan2(pos[1] - center[1], pos[0] - center[0]) + math.pi / 2)
        dis = pp.utils.game_math.distance(self.center, pos) / 5
        self.e['Sounds'].play(sound, angle=angle, distance=dis, volume=volume)

    def apply_shield(self, damage):
        shield_scale = self.e['State'].upgrade_stat('reinforced_steel') + 1
        for stack in list(self.guard_stacks):
            shield_amt = min(stack[2] * shield_scale, damage)   
            stack[2] -= shield_amt / shield_scale
            damage -= shield_amt 
            if stack[2] <= 0:
                self.guard_stacks.remove(stack)
        shield_amt = min(self.shield * shield_scale, damage)
        self.shield -= shield_amt / shield_scale
        damage -= shield_amt
        return damage
    
    def damage(self, damage, src_weapon=None):
        # scale damage taken based on the difficulty set
        damage = damage * self.e['State'].difficulty_set_stats['damage']

        if ((not self.iframes) and (not self.e['State'].effect_active('invincibility'))) and self.health:
            if self.health / self.max_health < 0.25:
                if random.random() < self.e['State'].upgrade_stat('close_call'):
                    self.e['Sounds'].play('blocked', volume=0.7)
                    return True
                
            if random.random() < self.weapon.enchant_stat('sturdy'):
                self.e['Sounds'].play('blocked', volume=0.7)
                return True
            
            self.e['Sounds'].play('player_hit', volume=0.5)

            self.damaged_in_wave = True

            damage = self.apply_shield(damage)

            self.health = max(0, self.health - damage)
            self.hurt = 1
            self.iframes = 1 * (self.e['State'].upgrade_stat('invincibility') + 1)
            for i in range(self.e['State'].upgrade_stat('thorns')):
                self.e['EntityGroups'].add(Bullet('blue', self.center, random.random() * math.pi * 2, advance=4, base_range=150, damage=2, speed=110), 'entities')
            if not self.health:
                if self.e['State'].upgrade_stat('revival'):
                    self.e['State'].owned_upgrades['revival'] -= 1
                    self.e['Sounds'].play('revive', volume=0.3)
                    for i in range(random.randint(5, 7)):
                        anim = Animation('flash', (self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-9, 6)))
                        anim.animation.update(random.random() * 0.6)
                        anim.flip[0] = random.choice([True, False])
                        self.e['EntityGroups'].add(anim, 'vfx')
                    spark_colors = [(38, 27, 46), (254, 252, 211)]
                    for i in range(24):
                        self.e['EntityGroups'].add(pp.vfx.Spark(self.center, random.random() * math.pi * 2, size=(random.randint(16, 20), random.randint(4, 6)), speed=random.random() * 70 + 20, decay=random.random() * 1.5 + 0.75, color=random.choice(spark_colors), z=0), 'vfx')
                    self.e['State'].notify('Revived!', font='small_font')
                    self.health = self.max_health * 0.5
                    self.iframes = 2 * (self.e['State'].upgrade_stat('invincibility') + 1)
                else:
                    self.die()
            self.e['Game'].freeze_stack.append([0.1, 0.25])
            if self.e['Settings'].screenshake:
                self.e['Game'].camera.screenshake = max(self.e['Game'].camera.screenshake, 0.25)
            return True
        
    def roll(self, vector, free=False):
        if not any(vector):
            vector = self.last_movement
            
        self.e['Sounds'].play('roll', volume=0.8)
        if not free:
            self.roll_cooldown = self.roll_cooldown_amt
        self.roll_direction = -1 if self.flip[0] else 1
        anim_dir = 1
        if vector[0] > 0:
            self.roll_direction = 1
        if vector[0] < 0:
            self.roll_direction = -1
            anim_dir = -1
        if not vector[0]:
            anim_dir = 0
        
        if (anim_dir == 1) or (not anim_dir):
            anim = Animation('turn', (self.center[0] - 6, self.pos[1] + self.size[1]))
            self.e['EntityGroups'].add(anim, 'vfx')
        if (anim_dir == -1) or (not anim_dir):
            anim = Animation('turn', (self.center[0] + 6, self.pos[1] + self.size[1]))
            anim.flip[0] = True
            self.e['EntityGroups'].add(anim, 'vfx')

        roll_force = 3 * (self.e['State'].upgrade_stat('leg_day') + 1)
        self.kb_stack = []
        self.kb_stack.append([math.atan2(vector[1], vector[0]), self.base_speed * roll_force])

        if self.e['State'].upgrade_stat('garys_charm') and (not self.e['State'].effect_active('garys_charm')):
            self.e['Game'].player.guard(1, 2)
            self.e['State'].add_effect('garys_charm', 16)
            self.e['Sounds'].play('shield_applied', volume=1.0)

        if self.partner[0]:
            self.partner[0].kb_stack.append([math.atan2(vector[1], vector[0]), self.base_speed * roll_force])
            self.partner[0].roll_direction = self.roll_direction
            self.partner[0].roll_angle = self.roll_angle

        self.roll_damaged = set()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if self.e['State'].effect_active('miasma'):
            self.miasma_cooldown -= self.e['Window'].dt
            if self.miasma_cooldown < 0:
                if self.e['State'].effects['miasma'][1] - self.e['State'].effects['miasma'][0] < 240:
                    self.miasma_cooldown += 5
                elif self.e['State'].effects['miasma'][1] - self.e['State'].effects['miasma'][0] < 270:
                    self.miasma_cooldown += 2.5
                elif self.e['State'].effects['miasma'][1] - self.e['State'].effects['miasma'][0] < 300:
                    self.miasma_cooldown += 1.25
                for i in range(10):
                    color = random.choice([(100, 97, 139), (121, 132, 157), (163, 179, 182)])
                    p = pp.vfx.Particle((self.center[0] + random.random() * 4 - 2, self.pos[1] + random.random() * 3 - 10), 'basep', (0, -8 + random.random() * 4), decay_rate=0.02, advance=0.3 + 0.4 * random.random(), colors={(255, 255, 255): color}, z=self.pos[1] + 0.52, behavior='smoke')
                    self.e['EntityGroups'].add(p, 'particles')
                self.e['Sounds'].play('cough', volume=0.35)
                self.damage(0.5)

        self.outline = (38, 27, 46) if (self.e['Settings'].setting('outline') == 'enabled') else None

        for stack in list(self.guard_stacks):
            stack[0] = max(0, stack[0] - self.e['Window'].dt)
            if stack[0] <= 0:
                self.guard_stacks.remove(stack)

        self.hurt = max(0, self.hurt - self.e['Window'].dt)
        self.iframes = max(0, self.iframes - self.e['Window'].dt)
        self.invisible = max(0, self.invisible - self.e['Window'].dt)

        if not self.partner[1]:
            self.partner[0] = None
        self.partner[1] = max(0, self.partner[1] - 1)

        self.e['State'].catalog_log('weapons', self.weapon.type)
        for enchant in list(self.weapon.enchants):
            if self.weapon.enchants[enchant][1]:
                self.e['State'].catalog_log('enchantments', enchant) 

        self.v_velocity += self.e['Window'].dt * self.gravity
        height_min = -48 if self.e['Transition'].level_end else 0
        self.height = max(height_min, self.height + self.v_velocity * self.e['Window'].dt)
        if self.height <= height_min:
            if (self.v_velocity < -100) and (not self.e['Transition'].level_end):
                self.e['Sounds'].play('land', volume=0.7)
                anim = Animation('turn', (self.center[0] - 6, self.pos[1] + self.size[1]))
                self.e['EntityGroups'].add(anim, 'vfx')
                anim = Animation('turn', (self.center[0] + 6, self.pos[1] + self.size[1]))
                anim.flip[0] = True
                self.e['EntityGroups'].add(anim, 'vfx')
                if self.e['State'].shopping and (not self.shop_landed):
                    self.shop_landed = True
                    if self.partner[0] and (self.e['State'].wave == 30):
                        self.partner[0].void_entry_dialoge()
            self.v_velocity = 0

        self.opacity = min(255, 255 + self.height * 8)

        movement = [0, 0]
        if (not self.dead) and (not self.e['Transition'].level_end) and (not self.e['State'].title) and (not self.e['State'].ui_busy):
            self.e['Game'].gm.apply_force((self.center[0], self.pos[1] + self.size[1]), 4, 4)

            if self.e['Game'].controller_mode:
                movement = self.e['Controllers'].read_stick('move_x', 'move_y')
                movement[0] *= self.speed * self.e['Window'].dt
                movement[1] *= self.speed * self.e['Window'].dt
            else:
                if self.e['Input'].holding('right'):
                    movement[0] += self.speed * self.e['Window'].dt
                if self.e['Input'].holding('left'):
                    movement[0] -= self.speed * self.e['Window'].dt
                if self.e['Input'].holding('down'):
                    movement[1] += self.speed * self.e['Window'].dt
                if self.e['Input'].holding('up'):
                    movement[1] -= self.speed * self.e['Window'].dt

                # make diagonal movement proportional
                if (movement[0] and movement[1]):
                    movement[0] /= math.sqrt(2)
                    movement[1] /= math.sqrt(2)

            self.weapon.update(self.e['Window'].dt)
            if self.alt_weapon:
                self.alt_weapon.update(self.e['Window'].dt)
            self.swap_cooldown = max(0, self.swap_cooldown - self.e['Window'].dt)

            if (self.e['Input'].pressed('swap_weapon') or (self.e['Game'].controller_mode and self.e['Controllers'].pressed('swap'))) and (not self.swap_cooldown) and self.alt_weapon:
                self.weapon, self.alt_weapon = self.alt_weapon, self.weapon
                self.swap_cooldown = self.swap_cooldown_amt
                self.e['Sounds'].play('swap', volume=1.0)
                self.e['HUD'].swap_offset = 16
                if self.e['Tutorial'].state == 5:
                    self.e['Tutorial'].advance()
                if self.e['State'].upgrade_stat('trigger_finger'):
                    if not self.weapon.attempt_secondary():
                        self.e['Sounds'].play('cooldown', volume=1.0)

            if (self.e['Input'].holding('shoot') or (self.e['Game'].controller_mode and self.e['Controllers'].holding('primary'))) and (not self.rolling):
                fired = self.weapon.attempt_fire()
                if fired and (self.e['Tutorial'].state == 1):
                    self.e['Tutorial'].advance()

            if (self.e['Input'].holding('secondary') or (self.e['Game'].controller_mode and self.e['Controllers'].holding('secondary'))) and (not self.rolling):
                if not self.weapon.attempt_secondary():
                    if self.e['Input'].pressed('secondary') or (self.e['Game'].controller_mode and self.e['Controllers'].pressed('secondary')):
                        self.e['Sounds'].play('cooldown', volume=1.0)
                elif self.e['Tutorial'].state == 2:
                    self.e['Tutorial'].advance()

            self.roll_cooldown = max(0, self.roll_cooldown - self.e['Window'].dt)
            if self.e['Input'].pressed('dodge') or (self.e['Game'].controller_mode and self.e['Controllers'].pressed('dodge')):
                if not self.roll_cooldown:
                    if self.e['Tutorial'].state == 3:
                        self.e['Tutorial'].advance()
                    self.roll(movement)

                    for i in range(self.e['State'].upgrade_stat('fatstep')):
                        self.e['EntityGroups'].add(Bullet('blue', (self.center[0], self.rect.bottom), random.random() * math.pi * 2, advance=4, base_range=150, damage=1.5, speed=110), 'entities')
                    if self.e['State'].upgrade_stat('fatstep'):
                        self.e['Sounds'].play('shoot', volume=0.25)

            if self.e['State'].effect_active('deathspiral'):
                self.deathspiral_cooldown -= self.e['Window'].dt
                if self.deathspiral_cooldown < 0:
                    self.deathspiral_cooldown += 0.05
                    self.e['EntityGroups'].add(Bullet('blue', self.center, (self.e['Window'].time * 12) % (math.pi * 2), advance=6, base_range=150, damage=1, speed=150), 'entities')
                    self.e['EntityGroups'].add(Bullet('blue', self.center, (self.e['Window'].time * 12) % (math.pi * 2) + math.pi, advance=6, base_range=150, damage=1, speed=150), 'entities')
                    self.e['Sounds'].play('shoot', volume=0.15)

        if not self.weapon.shoot_cooldown[0]:
            movement[0] *= self.e['State'].upgrade_stat('running_shoes') + 1
            movement[1] *= self.e['State'].upgrade_stat('running_shoes') + 1
        elif self.e['State'].upgrade_stat('turret'):
            movement[0] *= (1 - self.e['State'].upgrade_stat('turret'))
            movement[1] *= (1 - self.e['State'].upgrade_stat('turret'))

        kb_dt = self.e['Window'].dt
        if self.e['State'].effect_active('dash_slash'):
            kb_dt *= 2
            for i in range(10):
                if random.random() / 60 < self.e['Window'].dt:
                    self.e['EntityGroups'].add(pp.vfx.Spark(self.center, self.angle + math.pi + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=random.choice([(254, 252, 211), (191, 60, 96)]), z=0), 'vfx')
            if self.weapon.type == 'carnelianblade':
                if (not self.local_bullet) or (self.local_bullet.src_weapon != self.weapon) or (self.local_bullet.piercing < 99999):
                    self.local_bullet = Bullet('blue', self.center, self.angle, 0, 0, 1, 5, 99999999, self.weapon)
                for enemy in aoe_friendly_attack_range(self.center, 8):
                    self.local_bullet.attempt_damage(enemy)

        for kb in self.kb_stack[::-1]:
            movement[0] += math.cos(kb[0]) * kb[1] * kb_dt
            movement[1] += math.sin(kb[0]) * kb[1] * kb_dt
            kb[1] = max(0, kb[1] - kb_dt * 500)
            if not kb[1]:
                self.kb_stack.remove(kb)

        if self.roll_direction:
            self.roll_angle += self.roll_direction * self.e['Window'].dt * 20
            if (self.roll_angle > math.pi * 2) or (self.roll_angle < -math.pi * 2):
                self.roll_angle = 0
                self.roll_direction = 0
            self.rotation = -math.degrees(self.roll_angle)
            self.scale = [1, 0.5]
            self.config['offset'] = [-3, -5]
            if self.e['State'].upgrade_stat('spiked_helmet'):
                if self.grid_pos in self.e['Machines'].machine_map:
                    machine = self.e['Machines'].machine_map[self.grid_pos]
                    if machine not in self.roll_damaged:
                        machine.damage(self.e['State'].upgrade_stat('spiked_helmet'))
                        self.roll_damaged.add(machine)
        else:
            self.scale = [1, 1]
            self.config['offset'] = [-3, -14]

        if movement[0] > 0:
            if self.flip[0]:
                self.set_action('run_reverse')
            else:
                self.set_action('run')
            if not self.last_movement_flip:
                anim = Animation('turn', (self.center[0] - 6, self.pos[1] + self.size[1]))
                self.e['EntityGroups'].add(anim, 'vfx')
            self.last_movement_flip = True
        elif movement[0] < 0:
            if self.flip[0]:
                self.set_action('run')
            else:
                self.set_action('run_reverse')
            if self.last_movement_flip:
                anim = Animation('turn', (self.center[0] + 6, self.pos[1] + self.size[1]))
                anim.flip[0] = True
                self.e['EntityGroups'].add(anim, 'vfx')
            self.last_movement_flip = False
        elif movement[1] == 0:
            self.set_action('idle')
        else:
            self.set_action('run')
        if self.height:
            self.set_action('jump')

        if sum(movement):
            if self.e['Tutorial'].state == 0:
                self.e['Tutorial'].advance()
            self.moved = True

        movement_steps = math.ceil(math.sqrt(movement[0] ** 2 + movement[1] ** 2) / 4.5)
        for i in range(movement_steps):
            self.physics_update([movement[0] / movement_steps, movement[1] / movement_steps])

        # force map boundaries
        if self.pos[0] < 0:
            self.pos[0] = 0
        if self.pos[0] + self.size[0] > self.e['Tilemap'].dimensions[0] * self.e['Tilemap'].tile_size:
            self.pos[0] = self.e['Tilemap'].dimensions[0] * self.e['Tilemap'].tile_size - self.size[0]
        if self.pos[1] < 0:
            self.pos[1] = 0
        if self.pos[1] + self.size[1] > self.e['Tilemap'].dimensions[1] * self.e['Tilemap'].tile_size:
            self.pos[1] = self.e['Tilemap'].dimensions[1] * self.e['Tilemap'].tile_size - self.size[1]

        self.z = self.pos[1] / self.e['Tilemap'].tile_size

        mouse_offset = pygame.Vector2(self.e['Game'].mpos) + self.e['Game'].camera.pos - self.gun_center
        self.angle = math.atan2(mouse_offset.y, mouse_offset.x)

        self.hitbox = pygame.Rect(self.pos[0], self.pos[1] - 8, 9, 14)

        if any(movement):
            self.last_movement = tuple(movement)

        if self.e['State'].upgrade_stat('hothead'):
            for x in range(1 + self.e['State'].upgrade_stat('hothead') * 2):
                for y in range(1 + self.e['State'].upgrade_stat('hothead') * 2):
                    loc = (self.grid_pos[0] + x - self.e['State'].upgrade_stat('hothead'), self.grid_pos[1] + y - self.e['State'].upgrade_stat('hothead'))
                    if loc in self.e['Machines'].machine_map:
                        machine = self.e['Machines'].machine_map[loc]
                        if not machine.has_effect('flame'):
                            machine.apply_effect('flame', 4.2)

        if len(self.stored_powerups):
            self.e['State'].add_effect('storage', 100, hidden=True)
        else:
            self.e['State'].clear_effect('storage')
    
    @property
    def gun_center(self):
        return (self.center[0], self.pos[1] - 4)
    
    @property
    def img(self):
        if self.e['Settings'].setting('pink_player') == 'enabled':
            img = super().img
            return pygame.mask.from_surface(img).to_surface(setcolor=(255, 0, 255), unsetcolor=(0, 0, 0, 0))
        return super().img

    def renderz(self, *args, **kwargs):
        if not self.dead:
            self.e['Tilemap'].tree_visibility_rects.append(self.rect)

            if (((not self.iframes) and (not self.e['State'].effect_active('invincibility'))) or (random.random() < 0.7)) and (not self.invisible):
                super().renderz(*args, offset=(self.e['Game'].camera[0], self.e['Game'].camera[1] + self.height), group='default')

                weapon_img = self.weapon.img
                if abs((self.angle + math.pi) % (math.pi * 2) - math.pi) > math.pi / 2:
                    weapon_img = pygame.transform.flip(weapon_img, False, True)
                    self.flip[0] = True
                else:
                    self.flip[0] = False
                if not self.rolling:
                    weapon_img = pygame.transform.rotate(weapon_img, -math.degrees(self.angle))
                    weapon_img.set_alpha(self.opacity)
                    pos = (self.gun_center[0] - weapon_img.get_width() // 2 - self.e['Game'].camera[0], self.gun_center[1] - weapon_img.get_height() // 2 - self.e['Game'].camera[1] - self.height)
                    self.e['Renderer'].blit(weapon_img, pos, z=self.z + 0.01)

            if not self.e['Transition'].level_end:
                shadow_img = self.e['Assets'].images['misc']['shadow']
                self.e['Renderer'].blit(shadow_img, (self.center[0] - shadow_img.get_width() // 2 - self.e['Game'].camera[0], self.pos[1] + self.size[1] - shadow_img.get_height() // 2 - self.e['Game'].camera[1]), z=-99998)

TYPES.Player = Player