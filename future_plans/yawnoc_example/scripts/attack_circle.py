import math
import random

import pygame

from . import pygpen as pp

from .slash import Slash

class AttackCircle(pp.Element):
    def __init__(self, pos):
        super().__init__()

        self.origin = list(pos)
        self.damage = 1

        decay_scale = 1 / max(0.0001, (1 - self.e['State'].upgrade_stat('swordsmans_pendant')))
        self.circle_vfx = pp.vfx.Circle(list(pos), velocity=130, decay=0.9 * decay_scale, width=6, radius=0, color=(191, 60, 96), z=5980)
        self.circle_vfx_2 = pp.vfx.Circle(list(pos), velocity=130, decay=1.0 * decay_scale, width=6, radius=0, color=(254, 252, 211), z=5979)

    @property
    def rect(self):
        return pygame.Rect(self.origin[0] - self.circle_vfx.radius, self.origin[1] - self.circle_vfx.radius, self.circle_vfx.radius * 2, self.circle_vfx.radius * 2)

    def update(self, dt):
        player = self.e['Game'].player
        dis = pp.utils.game_math.distance(self.origin, player.center)
        if abs(dis - self.circle_vfx.radius) < 5:
            if not player.rolling:
                if player.damage(self.damage):
                    angle = math.atan2(player.center[1] - self.origin[1], player.center[0] - self.origin[0])
                    player.kb_stack.append([angle, 100])
                    self.e['EntityGroups'].add(Slash(player.center, angle + random.random() - 0.5, (20, 2)), 'vfx')
                    for i in range(5):
                        self.e['EntityGroups'].add(pp.vfx.Spark(player.center, angle + random.random() * 1.5 - 0.75, size=(random.randint(4, 6), 1), speed=random.random() * 100 + 120, decay=random.random() * 9 + 4, color=(254, 252, 211), z=0), 'vfx')
        self.circle_vfx_2.update(dt)
        return self.circle_vfx.update(dt)

    def renderz(self, group='default', offset=(0, 0)):
        if self.rect.colliderect(self.e['Game'].camera.rect):
            self.circle_vfx.renderz(group=group, offset=offset)
            if self.circle_vfx_2.velocity > 0:
                self.circle_vfx_2.renderz(group=group, offset=offset)