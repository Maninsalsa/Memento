import math

import pygame

from . import pygpen as pp

from .animation import Animation

class Transition(pp.ElementSingleton):
    def __init__(self):
        super().__init__()
        self.level_end = 0

        self.active = False
        self.inverted = False
        self.direction = -1
        self.transition_timer = 0.5
        self.diag = max(self.e['Game'].display.get_size()) * math.sqrt(2)

        self.callback = None

    def end_level(self, callback=None):
        self.e['Music'].fadeout(2.5)
        self.active = True
        if not self.level_end:
            self.level_end += self.e['Window'].dt
        self.inverted = True
        self.callback = callback
        self.e['Game'].player.v_velocity = 200
        if self.e['Game'].player.partner[0]:
            self.e['Game'].player.partner[0].v_velocity = 200
        self.e['Sounds'].play('jump', volume=0.8)

        player = self.e['Game'].player
        anim = Animation('turn', (player.center[0] - 6, player.pos[1] + player.size[1]))
        self.e['EntityGroups'].add(anim, 'vfx')
        anim = Animation('turn', (player.center[0] + 6, player.pos[1] + player.size[1]))
        anim.flip[0] = True
        self.e['EntityGroups'].add(anim, 'vfx')

    def transition(self, callback=None):
        self.direction = 1
        if callback:
            self.callback = callback
    
    def update(self):
        if self.level_end:
            self.level_end += self.e['Window'].dt
            if self.level_end > 2:
                self.transition()
                self.active = False

        self.transition_timer = max(0, min(0.5, self.transition_timer + self.e['Window'].dt * self.direction))
        if self.transition_timer >= 0.5:
            if self.callback:
                self.callback()
                self.callback = None
                self.direction = -1
            self.inverted = False
            self.level_end = 0

    @property
    def progress(self):
        return self.transition_timer * 2
    
    @property
    def floor_hole_radius(self):
        if self.level_end:
            return min(self.level_end, 0.5) * 64
        return 0

    def render(self):
        if self.level_end:
            self.e['Renderer'].renderf(pygame.draw.circle, (38, 27, 46), (self.e['Game'].player.center[0] - self.e['Game'].camera[0], self.e['Game'].player.center[1] - self.e['Game'].camera[1]), self.floor_hole_radius, group='default', z=self.e['Game'].player.z - 0.01)

        if self.progress:
            if self.inverted:
                self.e['Renderer'].renderf(pygame.draw.circle, (38, 27, 46), (self.e['Game'].display.get_width() // 2, self.e['Game'].display.get_height() // 2), self.diag / 2 * self.progress, group='ui', z=10010)
            else:
                surf = pygame.Surface(self.e['Game'].display.get_size())
                surf.fill((38, 27, 46))
                pygame.draw.circle(surf, (0, 0, 0), (self.e['Game'].display.get_width() // 2, self.e['Game'].display.get_height() // 2), self.diag / 2 * (1 - self.progress))
                surf.set_colorkey((0, 0, 0))
                self.e['Renderer'].blit(surf, (0, 0), group='ui', z=10010)