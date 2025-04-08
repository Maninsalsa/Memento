import math
import random

from . import pygpen as pp

SNOW_COUNT = 300
LEAF_COUNT = 30

class Snow(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.snow = []
        for i in range(SNOW_COUNT):
            # x, y, y offset, seeds, angle_log
            self.snow.append([random.random() * self.e['Game'].display.get_width(), (random.random() + 0.5) * self.e['Game'].display.get_height(), (random.random() + 0.5) * self.e['Game'].display.get_height(), (random.random(), random.random()), 0])

    def update(self):
        season = self.e['State'].season
        speed = 1 if season == 'winter' else 1.5
        if season in {'winter', 'fall'}:
            for i, particle in enumerate(self.snow):
                particle[1] += (particle[3][0] + 3) * self.e['Window'].dt * 3 * speed
                phase = math.sin((particle[3][1] + 1) * self.e['Window'].time * speed)
                particle[0] += phase * self.e['Window'].dt * 5 * speed
                particle[4] = math.floor((phase + 1) * 2.49)
                if season == 'fall':
                    particle[0] += self.e['Window'].dt * 3.5 * speed
                    if i >= LEAF_COUNT:
                        break

    def render(self):
        season = self.e['State'].season
        if season in {'winter', 'fall'}:
            for i, particle in enumerate(self.snow):
                if season == 'winter':
                    self.e['Game'].display.set_at((int(particle[0] - self.e['Game'].camera[0]) % self.e['Game'].display.get_width(), int(particle[1] - particle[2] - self.e['Game'].camera[1]) % int(self.e['Game'].display.get_height() * 1.5)), (254, 252, 211))
                elif season == 'fall':
                    type_offset = 5 if i % 2 else 0
                    self.e['Game'].display.blit(self.e['Assets'].images['leaf'][str(particle[4] + type_offset)], ((particle[0] - self.e['Game'].camera[0]) % self.e['Game'].display.get_width(), (particle[1] - particle[2] - self.e['Game'].camera[1]) % int(self.e['Game'].display.get_height() * 1.5)))
                    if i >= LEAF_COUNT:
                        break