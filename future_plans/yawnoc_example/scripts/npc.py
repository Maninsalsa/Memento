import math
import random

import pygame

from .pygpen import Entity, gfx_util, game_math
from .pygpen.utils.game_math import distance

from .speech_bubble import SpeechBubble
from . import tilemap

DIALOGUE = {
    'gary': ['A fine weapon you have, but they can always be improved!'],
    'daisy': ['I\'ve been doing some truly ribbit-ing field research on those pesky machines.'],
    'goat': ['*strange noises*'],
}

INWORLD_DIALOGUE = {
    'gary': ['Welcome back!', 'How goes the fight?'],
    'daisy': ['These machines have a peculiar design...', 'There seem to be rules to their behavior.', 'They appear to be powered by another dimension?', 'Have you seen any new machines lately?'],
}

DAISY_DIALOGUE = {
    'summer': [
        'The machines in this area appear to live and die by two different rulesets. Their names came to me in a dream the other day while I was slumbering.',
        'It appears as if a machine can have up to 8 neighbors. The number of existing neighbors determines what the machines will do next.',
        'I\'ve named the more common ruleset that dictates machine behavior Conway\'s Game of Life.',
        'A machine with anything other than 2 or 3 neighbors will disappear. If a place has exactly 3 neighbors, a machine will appear.',
        '<img>summer_sheet<text>Here are my notes for the area.',
        'HighLife is the rarer ruleset that I\'ve seen around here. It\'s like Conway\'s Game of Life, except machines will also appear in a place with 5 or 6 neighbors.',
        'Talk to me again when you visit another area. I\'m always working on my research!',
    ],
    'fall': [
        'The machines in this area primarily follow one ruleset with two levels of activity. I call it Brian\'s Brain.',
        'All machines are individually progressing towards death regardless of their neighbors.',
        'If a place has not had a machine in it for a bit and has exactly 2 new neighbors, a machine will appear.',
        'There are "Spawner" machines that violate these rules by not dying. As a result of hanging around, they end up creating lots of new machines. Destroy them first.',
        '<img>fall_sheet<text>Here are my notes for the area.',
        'I\'ve named the higher level of activity Brian\'s Migraine because the chaos gave me a headache. Spawners will create way more machines when affected by this.',
        'The patterns created around here are highly mobile and volatile. You must take care to eliminate them before they get out of control.',
    ],
    'winter': [
        'I didn\'t like the name I got from the dream this time. It was B5/S3456, but I don\'t like it, so I decided to call the local ruleset Blobell.',
        'A machine with less than 3 or greater than 6 neighbors will die and a machine will appear in a place that has 5 neighbors.',
        '<img>winter_sheet<text>Here are my notes for the area.',
        'I\'ve named the rare variant Blursed. It\'s the same as Blobell except machines will also appear with 7 or 8 neighbors and survive with 7 neighbors.',
        'This mostly results in higher machine density where they already exist.',
        'The machines in this area don\'t move around much unless attacked. They\'re more defensive and harder to kill as well.',
        'It\'s like they\'re trying to hibernate.',
    ],
    'void': [
        'This is such a strange place. I\'ve only seen one ruleset that the machines follow around here.',
        'I call it LowDeath. Machines with 2, 3, or 8 neighbors will survive and machines will appear in a place with 3, 6, or 8 neighbors.',
        'Many of the primitive patterns will behave the same as Conway\'s Game of Life, but once more machines are involved, it\'s much more chaotic.',
        '<img>void_sheet<text>Here are my notes for the area.',
        'I suspect there\'s something else going on in this area that I\'ve missed.',
        'Be careful out there.',
    ],
}

NAMES = {
    'gary': 'Gary',
    'daisy': 'Daisy',
    'goat': 'Suspicious Goat',
}

class NPC(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.type == 'gary':
            self.z = (self.pos[1] + 47.01) / self.e['Tilemap'].tile_size
        else:
            # todo: add height offset similar to player
            self.z = (self.pos[1] + self.size[1] - 5) / self.e['Tilemap'].tile_size

        self.name = 'unknown'
        if self.type in NAMES:
            self.name = NAMES[self.type]

        self.spoken = False
        self.speech_bubble = None

        self.last_frame = self.animation.frame

    @property
    def head_origin(self):
        origin = self.pos

        if self.type == 'gary':
            origin = (self.pos[0] + 31, self.pos[1] + 19)
        
        elif self.type == 'daisy':
            origin = (self.pos[0], self.pos[1] + 5)

        return origin

    @property
    def hitbox_origin(self):
        origin = self.pos

        if self.type == 'gary':
            origin = (self.pos[0] + 30, self.pos[1] + 38)

        elif self.type == 'daisy':
            origin = (self.pos[0] + 4, self.pos[1] + 5)

        elif self.type == 'goat':
            origin = (self.pos[0] + 6, self.pos[1] + 4)

        return origin

    def interact(self):
        if self.e['State'].guide_progress['upgrade_purchase'] and self.e['State'].guide_progress['daisy_talked'] and (not self.e['State'].guide_progress['enchant_purchase']) and (self.e['State'].wave > 2) and (self.e['State'].scrap >= 20) and (self.type == 'gary'):
            self.e['State'].dialogue = [self, ['The hearts of weapons are all connected.', 'As an arcane blacksmith, I can enhance weapons with enchantments that cross the boundaries of time and space.', 'Let me see what you\'ve got.']]
        elif self.type in DIALOGUE:
            self.e['State'].dialogue = [self, DIALOGUE[self.type].copy()]
            if (self.type == 'daisy') and (self.e['State'].season in DAISY_DIALOGUE):
                self.e['State'].dialogue[1] += DAISY_DIALOGUE[self.e['State'].season]
                if not self.e['State'].guide_progress['daisy_talked']:
                    self.e['State'].guide_progress['daisy_talked'] = 1
                    self.e['State'].save()
        
        if self.type == 'goat':
            self.e['Game'].player.play_from('goat', self.center, volume=0.8)
            self.e['Steamworks'].grant_achievement('father')

    def update(self, dt):
        super().update(dt)

        if self.type == 'gary':
            if (self.animation.frame == 1) and (self.last_frame != 1):
                dis = game_math.distance(self.center, self.e['Game'].player.center)
                vol = max(0, (300 - dis) / 300 * 0.35)
                self.e['Game'].player.play_from('clank', self.center, volume=vol)
            if self.e['State'].guide_progress['upgrade_purchase'] and self.e['State'].guide_progress['daisy_talked'] and (not self.e['State'].guide_progress['enchant_purchase']) and (self.e['State'].wave > 2) and (self.e['State'].scrap >= 20):
                self.e['HUD'].guide_target = tuple(self.hitbox_origin)
        elif self.type == 'daisy':
            if self.e['State'].guide_progress['upgrade_purchase'] and (not self.e['State'].guide_progress['daisy_talked']):
                self.e['HUD'].guide_target = tuple(self.hitbox_origin)
        self.last_frame = self.animation.frame

        player_distance = distance(self.e['Game'].player.pos[:2], self.hitbox_origin)
        if player_distance < 14:
            if self.e['State'].closest_entity[1] > player_distance:
                self.e['State'].closest_entity = [self, player_distance]

        self.outline = None
        if self.e['State'].closest_entity[0] == self:
            self.outline = (38, 27, 46)
        
        if self.type in INWORLD_DIALOGUE:
            if player_distance < 140:
                if not self.spoken:
                    self.spoken = True
                    self.speech_bubble = SpeechBubble(random.choice(INWORLD_DIALOGUE[self.type]))

    def renderz(self, offset=(0, 0), group='default'):
        super().renderz(offset=offset, group=group)

        if self.type == 'gary':
            self.e['Renderer'].blit(self.e['Assets'].images['misc']['gary_tail'], self.topleft(offset), z=-99997, group=group)
            if self.outline:
                self.e['Renderer'].renderf(gfx_util.outline, self.e['Assets'].images['misc']['gary_tail'], self.topleft(offset), self.outline, z=-99997.00001, group=group)
        else:
            shadow_img = self.e['Assets'].images['misc']['shadow']
            self.e['Renderer'].blit(shadow_img, (self.center[0] - shadow_img.get_width() // 2 - self.e['Game'].camera[0], self.pos[1] + self.size[1] - shadow_img.get_height() // 2 - self.e['Game'].camera[1]), z=-99998)

        if self.speech_bubble:
            self.speech_bubble.render(self.head_origin)
            if not self.speech_bubble.text:
                self.speech_bubble = None

tilemap.ENTITY_CLASSES['npc'] = NPC