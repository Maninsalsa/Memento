import time
import math
import random

import pygame

from . import pygpen as pp
from .pygpen.vfx import Particle

from .physics_entity import PhysicsEntity
from .weapon import Weapon
from .animation import Animation
from .speech_bubble import SpeechBubble
from .const import TYPES
from . import tilemap

BOSS_NAMES = {
    'jim': 'Jim',
    'oswald': 'Oswald',
    'hazel': 'Hazel',
}

DIALOGUE = {
    'jim': ['...', 'Wha-', 'What just happened?', 'I saw the machines invading the forest and everything went dark.', 'Something isn\'t right.'],
    'oswald': ['...', 'I think I blacked out.', 'I was fighting in a dark place with glints of steel.', 'I don\'t know what\'s causing all of this, but these machines must be expelled from the forest!'],
    'hazel': ['...', 'I made it to the dimension of the machines before.', 'It\'s a dark place, but I believe it\'s where they\'ve come from.', 'I found the eye of the storm and I don\'t remember anything since.', 'I know we\'re close.'],
}

VOID_ENTRY_DIALOGUE = {
    'jim': ['This is looking sketchy.', 'I think we\'re close to wherever all these machines are coming from.'],
    'oswald': ['...', 'This place again.', 'Yep, this is where we need to be.'],
    'hazel': ['We\'re getting close to the eye.', 'All the machines seem to be coming from this area.'],
}

STATS = {
    'jim': {
        'friend_health': 5.5,
        'enemy_health': 50,
        'weapon': 'pistol',
        'range': 12 * 10,
    },
    'oswald': {
        'friend_health': 7.5,
        'enemy_health': 90,
        'weapon': 'shotgun',
        'range': 12 * 6,
    },
    'hazel': {
        'friend_health': 4.5,
        'enemy_health': 150,
        'weapon': 'rifle',
        'range': 12 * 9,
    },
}

GUN_OFFSETS = {
    'jim': 0,
    'oswald': 5,
    'hazel': 6,
}

RECRUIT_DIALOGUE = {
    'jim': ['Let\'s go blast \'em machines!', 'Always happy to help!'],
    'oswald': ['Alright.', 'More scrap for the pile then.', 'Someday I\'ll return to my burrow.'],
    'hazel': ['The eye...', 'I think Jim is afraid of me.', 'We\'ve got a good shot this time!', 'We\'ve got this!'],
}

class Frenemy(PhysicsEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.weapon = Weapon(STATS[self.type]['weapon'], self)

        self.camping = self.e['State'].shopping != 0

        if self.camping and (self.type == 'hazel'):
            self.e['Steamworks'].grant_achievement('friends')

        self.friendly = self.camping
        self.alt_weapon = None
        self.revived = False
        self.alerted = False

        self.base_speed = 50
        self.angle = 0

        self.health = self.max_health
        self.z = 0
        self.height = 0

        self.set_action('idle_shadow')

        self.path = None

        self.range = STATS[self.type]['range']

        self.dead = False
        self.hurt = 0
        self.fallen_timer = 0

        self.kb_stack = []

        self.roll_direction = 0
        self.roll_angle = 0
        self.v_velocity = 0
        self.gravity = -300
        self.invisible = 0

        self.base_offset = self.config['offset'].copy()

        self.speech_bubble = None

    def heal(self, amt):
        self.health = min(self.health + amt, self.max_health)

    @property
    def rect(self):
        hitbox_growth = self.e['State'].upgrade_stat('meatshield') if self.friendly else 0
        return pygame.Rect(self.pos[0] - hitbox_growth, self.pos[1] - hitbox_growth, self.size[0] + hitbox_growth * 2, self.size[1] + hitbox_growth * 2)

    @property
    def weight(self):
        return 1 if self.friendly else 3

    @property
    def max_health(self):
        if self.friendly:
            return STATS[self.type]['friend_health'] + self.e['State'].upgrade_stat('chestplate')
        return STATS[self.type]['enemy_health'] * self.e['State'].difficulty_set_stats['enemy_health']

    @property
    def name(self):
        return BOSS_NAMES[self.type]
    
    @property
    def rolling(self):
        return self.roll_direction != 0
    
    @property
    def hitbox_radius(self):
        return 10
    
    def apply_effect(self, effect_id, duration, src_weapon=None):
        pass

    def destroy(self):
        self.dead = True

    def damage(self, damage, src_weapon=None):
        if self.friendly:
            # scale damage taken based on the difficulty set if friendly
            damage = damage * self.e['State'].difficulty_set_stats['damage']
            if self.hurt or self.e['State'].effect_active('invincibility'):
                return False
        else:
            if self.health == self.max_health:
                damage *= (self.e['State'].upgrade_stat('sledgehammer') + 1)
            if src_weapon:
                damage *= (src_weapon.enchant_stat('fmj') + 1)
        self.e['Game'].player.process_damage_applied(self, damage)
        if self.health and (damage >= self.health):
            self.e['Game'].player.play_from('npc_death', self.center, volume=0.6)
            if src_weapon and (random.random() < src_weapon.enchant_stat('hitrun')):
                self.e['State'].add_effect('swiftness', 3)
                self.e['Sounds'].play('powerup', volume=0.35)
        self.health = max(0, self.health - damage)
        self.hurt = 0.3
        for i in range(random.randint(1, 3)):
            anim = Animation('flash', (self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-9, 6)))
            anim.animation.update(random.random() * 0.3 + 0.3)
            anim.flip[0] = random.choice([True, False])
            self.e['EntityGroups'].add(anim, 'vfx')
        self.e['Game'].player.play_from('machine_hit', self.center, volume=0.7)
        return True
    
    @property
    def action_suffix(self):
        if self.friendly:
            return ''
        return '_shadow'
    
    def interact(self):
        self.camping = False
        self.speech_bubble = SpeechBubble(random.choice(RECRUIT_DIALOGUE[self.type]))
        # detach any existing partner
        if self.e['Game'].player.partner[0]:
            self.e['Game'].player.partner[0].camping = True
            self.e['Game'].player.partner = [None, 0]
        self.e['HUD'].new_team_alert(self)

    def void_entry_dialoge(self):
        self.e['State'].dialogue = [self, VOID_ENTRY_DIALOGUE[self.type].copy()]

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        self.hurt = max(0, self.hurt - self.e['Window'].dt)
        self.invisible = max(0, self.invisible - self.e['Window'].dt)

        distance = pp.game_math.distance(self.e['Game'].player.center, self.rect.center)

        if self.friendly and (not self.camping):
            self.e['Game'].player.partner = [self, 1]
            self.weapon.inaccuracy = 1

        if not self.friendly:
            self.e['HUD'].boss = self

            self.e['Tilemap'].tree_visibility_rects.append(self.rect)

            self.weapon.inaccuracy = 1 + self.e['State'].upgrade_stat('smokescreen')

            if (not self.e['Machines'].active_enemies_remaining) and (self.fallen_timer > 2.5):
                if distance < 24:
                    # detach any existing frenemies
                    if self.e['Game'].player.partner[0]:
                        self.e['Game'].player.partner[0].camping = True
                        self.e['Game'].player.partner = [None, 0]

                    self.friendly = True
                    for i in range(20):
                        color = random.choice([(100, 97, 139), (121, 132, 157), (163, 179, 182)])
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 40 + 10
                        p = Particle((self.center[0] + random.randint(-6, 6), self.center[1] + random.randint(-4, 4)), 'basep', (math.cos(angle) * speed, math.sin(angle) * speed), decay_rate=0.5, advance=0.2 + 0.4 * random.random(), colors={(255, 255, 255): color}, z=self.z + 0.005, behavior='smoke')
                        self.e['EntityGroups'].add(p, 'particles')
                    self.health = self.max_health
                    self.e['State'].dialogue = [self, DIALOGUE[self.type].copy()]
                    self.kb_stack = []
                    self.revived = True
                else:
                    self.e['HUD'].guide_target = tuple(self.center)

        if (not self.e['State'].ui_busy) and self.revived and (not self.alerted):
            self.e['HUD'].new_team_alert(self)
            self.alerted = True

        movement = [0, 0]

        if self.health:
            self.v_velocity += self.e['Window'].dt * self.gravity
            height_min = -48 if self.e['Transition'].level_end else 0
            self.height = max(height_min, self.height + self.v_velocity * self.e['Window'].dt)
            if self.height <= height_min:
                if (self.v_velocity < -100) and (not self.e['Transition'].level_end):
                    anim = Animation('turn', (self.center[0] - 6, self.pos[1] + self.size[1]))
                    self.e['EntityGroups'].add(anim, 'vfx')
                    anim = Animation('turn', (self.center[0] + 6, self.pos[1] + self.size[1]))
                    anim.flip[0] = True
                    self.e['EntityGroups'].add(anim, 'vfx')
                self.height = height_min
                self.v_velocity = 0

            self.opacity = min(255, 255 + self.height * 8)

            if self.roll_direction:
                self.roll_angle += self.roll_direction * self.e['Window'].dt * 20
                if (self.roll_angle > math.pi * 2) or (self.roll_angle < -math.pi * 2):
                    self.roll_angle = 0
                    self.roll_direction = 0
                self.rotation = -math.degrees(self.roll_angle)
                self.scale = [1, 0.5]
                self.config['offset'] = [self.base_offset[0], self.base_offset[1] * 0.25]
            else:
                self.scale = [1, 1]
                self.config['offset'] = self.base_offset

            if not self.friendly:
                target = None
                closest_space = self.e['Tilemap'].closest_space(self.rect.center)
                player_space = self.e['Tilemap'].closest_space(self.e['Game'].player.center)

                # verify that both paths are in-bounds since the a-star algorithm will hang if the target is unreachable
                if not (self.e['Tilemap'].in_bounds(closest_space) and self.e['Tilemap'].in_bounds(player_space)):
                    return True

                line_of_sight = not self.e['Tilemap'].physics_gridline(closest_space, player_space, include_gaps=False)
                # apply astar path if reasonable
                if (distance >= self.range) or (not line_of_sight):
                    # create new path if no valid old path, entity is close to next point, or player moved
                    if (not self.path) or (pp.game_math.distance(self.path[2], closest_space) < 1.5) or (pp.game_math.distance(self.path[-1], player_space) > 1.5):
                        self.path = list(self.e['Tilemap'].pathfinder.astar(closest_space, player_space))
                        if len(self.path) < 3:
                            self.path = None
                    if self.path:
                        target = ((self.path[2][0] + 0.5) * self.e['Tilemap'].tile_size, (self.path[2][1] + 0.5) * self.e['Tilemap'].tile_size)
                        angle = math.atan2(target[1] - self.rect.center[1], target[0] - self.rect.center[0])
                    else:
                        target = self.e['Game'].player.center
                        angle = math.atan2(target[1] - self.rect.center[1], target[0] - self.rect.center[0])

                    movement = [math.cos(angle) * self.base_speed * self.e['Window'].dt, math.sin(angle) * self.base_speed * self.e['Window'].dt]
                
                elif distance < self.range - 12 * 3:
                    target = self.e['Game'].player.center
                    angle = math.atan2(target[1] - self.rect.center[1], target[0] - self.rect.center[0]) + math.pi
                    movement = [math.cos(angle) * self.base_speed * self.e['Window'].dt, math.sin(angle) * self.base_speed * self.e['Window'].dt]

            elif self.camping:
                player_distance = pp.game_math.distance(self.e['Game'].player.pos[:2], self.center)
                if player_distance < 14:
                    if self.e['State'].closest_entity[1] > player_distance:
                        self.e['State'].closest_entity = [self, player_distance]
            
            elif (distance > 14) and (not self.e['State'].ui_busy):
                target = self.e['Game'].player.center
                angle = math.atan2(target[1] - self.rect.center[1], target[0] - self.rect.center[0])
                speed = self.e['Game'].player.speed + max(0, (distance - 16) * 4)
                movement = [math.cos(angle) * speed * self.e['Window'].dt, math.sin(angle) * speed * self.e['Window'].dt]
                
                # handle flip when it doesn't have a gun
                if self.revived:
                    if movement[0] > 0:
                        self.flip[0] = False
                    elif movement[0] < 0:
                        self.flip[0] = True

            kb_dt = self.e['Window'].dt
            if self.e['State'].effect_active('dash_slash') and self.friendly:
                kb_dt *= 2
                for i in range(10):
                    if random.random() / 60 < self.e['Window'].dt:
                        self.e['EntityGroups'].add(pp.vfx.Spark(self.center, self.angle + math.pi + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=random.choice([(254, 252, 211), (191, 60, 96)]), z=0), 'vfx')
            for kb in self.kb_stack[::-1]:
                movement[0] += math.cos(kb[0]) * kb[1] * kb_dt / self.weight
                movement[1] += math.sin(kb[0]) * kb[1] * kb_dt / self.weight
                kb[1] = max(0, kb[1] - kb_dt * 500)
                if not kb[1]:
                    self.kb_stack.remove(kb)

            if movement != [0, 0]:
                if movement[0] > 0:
                    if self.flip[0]:
                        self.set_action(f'run_reverse{self.action_suffix}')
                    else:
                        self.set_action(f'run{self.action_suffix}')
                elif movement[0] < 0:
                    if self.flip[0]:
                        self.set_action(f'run{self.action_suffix}')
                    else:
                        self.set_action(f'run_reverse{self.action_suffix}')
                else:
                    self.set_action(f'run{self.action_suffix}')
            else:
                self.set_action(f'idle{self.action_suffix}')

            self.weapon.update(self.e['Window'].dt)
            if not self.friendly:
                if line_of_sight and (time.time() - self.e['Machines'].wave_start > 2):
                    self.weapon.attempt_fire()

                self.physics_update(movement)
                self.angle = math.atan2(self.e['Game'].player.pos[1] - self.pos[1], self.e['Game'].player.pos[0] - self.pos[0])
            elif not self.camping:
                self.pos[0] += movement[0]
                self.pos[1] += movement[1]
                mouse_offset = pygame.Vector2(self.e['Game'].mpos) + self.e['Game'].camera.pos - self.gun_center
                self.angle = math.atan2(mouse_offset.y, mouse_offset.x)
                if (self.e['Input'].holding('shoot') or (self.e['Game'].controller_mode and self.e['Controllers'].holding('primary'))) and (not self.rolling) and self.weapon and (not self.revived) and (not self.e['State'].ui_busy) and (not self.e['Transition'].level_end) and (not self.e['Game'].player.dead):
                    self.weapon.attempt_fire(damage_scale=0.35)
            
        else:
            self.set_action(f'fall{self.action_suffix}')
            self.fallen_timer += self.e['Window'].dt

        if self.height and ('fall' not in self.action):
            self.set_action(f'jump{self.action_suffix}')

        self.z = (self.rect.bottom - 5) / self.e['Tilemap'].tile_size

        # add info for aim assist
        if (not self.friendly) and self.health and self.e['Settings'].aim_assist:
            player = self.e['Game'].player
            if pp.game_math.fast_range_check(player.center, self.center, player.weapon.max_range):
                angle = math.atan2(self.center[1] - player.center[1], self.center[0] - player.center[0])
                self.e['Machines'].machines_in_range.append((angle, len(self.e['Machines'].machines_in_range), self))

        self.outline = None
        if (self.e['Settings'].setting('outline') == 'enabled') and self.friendly and (not self.camping):
            self.outline = (38, 27, 46)
        if self.e['State'].closest_entity[0] == self:
            self.outline = (38, 27, 46)

        return self.dead

    @property
    def gun_center(self):
        return (self.center[0], self.pos[1] + 1)

    def renderz(self, *args, **kwargs):
        if not self.invisible:
            super().renderz(*args, offset=(self.e['Game'].camera[0], self.e['Game'].camera[1] + self.height), group='default')

            if self.speech_bubble:
                self.speech_bubble.render((self.center[0], self.pos[1]))
                if not self.speech_bubble.text:
                    self.speech_bubble = None

            if self.health and (not self.revived):
                weapon_img = self.weapon.img
                if abs((self.angle + math.pi) % (math.pi * 2) - math.pi) > math.pi / 2:
                    weapon_img = pygame.transform.flip(weapon_img, False, True)
                    self.flip[0] = True
                else:
                    self.flip[0] = False
                
                if not (self.rolling or self.camping):
                    weapon_img = pygame.transform.rotate(weapon_img, -math.degrees(self.angle))
                    weapon_img.set_alpha(self.opacity)
                    pos = (self.gun_center[0] - weapon_img.get_width() // 2 - self.e['Game'].camera[0], self.gun_center[1] - weapon_img.get_height() // 2 - self.e['Game'].camera[1] - self.height + GUN_OFFSETS[self.type])
                    self.e['Renderer'].blit(weapon_img, pos, z=self.z + 0.01)
            
            elif self.animation.finished:
                for i in range(5):
                    angle = math.pi * 2 * i / 5
                    star_img = self.e['Assets'].images['misc']['star']
                    t = time.time() * 2.1
                    pos = (self.center[0] + math.cos(angle + t) * 6 - star_img.get_width() // 2 - self.e['Game'].camera[0], self.pos[1] - 2 + math.sin(angle + t) * 6 - star_img.get_height() // 2 - self.e['Game'].camera[1])
                    z = self.z + 0.01 if math.sin(angle + t) > 0 else self.z - 0.01
                    self.e['Renderer'].blit(star_img, pos, z=z)
    
        shadow_img = self.e['Assets'].images['misc']['shadow']
        self.e['Renderer'].blit(shadow_img, (self.center[0] - shadow_img.get_width() // 2 - self.e['Game'].camera[0], self.pos[1] + self.size[1] - shadow_img.get_height() // 2 - self.e['Game'].camera[1]), z=-99998)

tilemap.ENTITY_CLASSES['frenemy'] = Frenemy

TYPES.Frenemy = Frenemy