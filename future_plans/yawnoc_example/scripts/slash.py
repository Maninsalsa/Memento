import math

import pygame

from . import pygpen as pp

class Slash(pp.Element):
    def __init__(self, pos, angle, dimensions, decay=20, speed=1.5, color=(254, 252, 211), group='default', z=None):
        super().__init__()
        self.pos = list(pos)
        self.size = list(dimensions)
        self.ratio = self.size[0] / self.size[1] * speed
        self.decay = decay
        self.color = color
        self.angle = angle
        self.group = group
        self.z = z

    def update(self, dt):
        self.size[1] = max(0, self.size[1] - self.decay * dt)
        self.size[0] += self.decay * dt * self.ratio 
        if not self.size[1]:
            return True

    def renderz(self, offset=(0, 0), group='default'):
        # hack for ui rendering
        if self.group != 'default':
            offset = (0, 0)

        base_pos = [self.pos[0] - offset[0], self.pos[1] - offset[1]]

        points = [
            pp.utils.game_math.advance(base_pos.copy(), self.angle, self.size[0]),
            pp.utils.game_math.advance(base_pos.copy(), self.angle + math.pi / 2, self.size[1]),
            pp.utils.game_math.advance(base_pos.copy(), self.angle + math.pi, self.size[0]),
            pp.utils.game_math.advance(base_pos.copy(), self.angle - math.pi / 2, self.size[1]),
        ]

        self.e['Renderer'].renderf(pygame.draw.polygon, self.color, points, group=self.group if (self.group != 'default') else group, z=self.z if (self.z != None) else self.pos[1] / self.e['Tilemap'].tile_size + 10)