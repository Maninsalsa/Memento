import random

import pygame

from . import pygpen as pp

class BloodBG(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.regenerate()

    def regenerate(self):
        self.surf = pygame.Surface(self.e['Game'].display.get_size(), pygame.SRCALPHA)

        self.blood_drips = []
        for i in range(51):
            pygame.draw.circle(self.surf, (191, 60, 96), (i / 50 * self.e['Game'].display.get_width(), 0), random.randint(4, 8))
            
            if random.random() < 0.4:
                self.blood_drips.append([i / 50 * self.e['Game'].display.get_width(), 0, random.random() * 2.5 + 1.5, random.random() * 3 + 3])

    def update(self, dt):
        for drip in self.blood_drips:
            drip[1] += dt * drip[3]
            drip[2] -= dt * 0.2
            if drip[2] >= 1.5:
                pygame.draw.circle(self.surf, (191, 60, 96), (drip[0], drip[1]), drip[2])
            elif drip[2] >= 1:
                self.surf.set_at((drip[0], drip[1]), (191, 60, 96))
