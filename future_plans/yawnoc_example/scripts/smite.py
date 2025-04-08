import math
import random

import pygame

from . import pygpen as pp

from .const import TYPES

class Smite(pp.ElementSingleton):
    def __init__(self, target_cell):
        super().__init__()

        self.target = target_cell
        self.time = 0

        self.range = 20

        spark_colors = [(38, 27, 46), (254, 252, 211)]
        self.e['EntityGroups'].add(pp.vfx.Circle(self.center, velocity=100, decay=2.5, width=4, radius=0, color=(254, 252, 211), z=5980), 'vfx')
        self.e['EntityGroups'].add(pp.vfx.Circle(self.center, velocity=250, decay=2.9, width=6, radius=0, color=(38, 27, 46), z=5978), 'vfx')
        for i in range(18):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.center, random.random() * math.pi * 2, size=(random.randint(5, 9), random.randint(1, 2)), speed=random.random() * 120 + 120, decay=random.random() * 3 + 0.5, color=random.choice(spark_colors), z=5981), 'vfx')
        for machine in list(self.e['Machines'].machine_map.values()):
            if pp.utils.game_math.distance(machine.center, self.center) < self.range:
                machine.damage(2)
        if 'enemies' in self.e['EntityGroups'].groups:
            for entity in self.e['EntityGroups'].groups['enemies']:
                if type(entity) == TYPES.CentipedeRig:
                    if pp.utils.game_math.distance(entity.segments[0], self.center) < self.range:
                        entity.damage(2)
        self.e['Game'].player.play_from('boom', self.center, volume=1.0)

        self.generate_path()

    @property
    def center(self):
        return ((self.target[0] + 0.5) * self.e['Tilemap'].tile_size, (self.target[1] + 0.5) * self.e['Tilemap'].tile_size)
    
    def update(self, dt):
        self.time += dt
        if self.time < 0.26:
            if (self.time % 0.05) > ((self.time + dt) % 0.05):
                self.generate_path()
        if self.time > 0.5:
            return True
        
    def generate_path(self):
        self.path = [
            (self.center[0], self.center[1]),
            (self.center[0] - 2 + random.random() * 4, self.center[1] - 10 + random.random() * 4),
            (self.center[0] - 4 + random.random() * 8, self.center[1] - 24 + random.random() * 6),
            (self.center[0] - 8 + random.random() * 16, self.center[1] - 42 + random.random() * 8),
            (self.center[0] - 10 + random.random() * 20, self.center[1] - 62 + random.random() * 10),
            (self.center[0] - 7 + random.random() * 14, self.center[1] - 80 + random.random() * 7),
            (self.center[0] - 3 + random.random() * 6, self.center[1] - 92 + random.random() * 4),
            (self.center[0] - 2 + random.random() * 4, self.center[1] - 100),
        ]

    def renderz(self, group='default', offset=(0, 0)):
        points = []
        width_scale = min(1, (0.5 - self.time) * 10)
        for i, point in enumerate(self.path):
            if i == len(self.path) - 1:
                i = 0
            points.append((point[0] - offset[0] - i * width_scale, point[1] - offset[1]))
        for i, point in list(enumerate(self.path))[::-1]:
            if i in {0, len(self.path) - 1}:
                continue
            points.append((point[0] - offset[0] + i * width_scale, point[1] - offset[1]))

        color = (254, 252, 211)
        if self.time < 0.05:
            color = (38, 27, 46)
        self.e['Renderer'].renderf(pygame.draw.polygon, color, points, group=group, z=self.target[1] + 0.6)