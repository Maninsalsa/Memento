import math

import pygame

from . import pygpen as pp

class HighlifeMap(pp.ElementSingleton):
    def __init__(self):
        super().__init__()
        tile_size = self.e['Tilemap'].tile_size
        self.center = ((self.e['Tilemap'].dimensions[0] // 2) * tile_size, (self.e['Tilemap'].dimensions[1] // 2) * tile_size)

    def render(self):
        axis_length = min(1, self.e['Machines'].high_life_time * 1.5)
        axis_length_2 = min(1, max(0, self.e['Machines'].high_life_time * 1.5 - 1))
        tile_size = self.e['Tilemap'].tile_size
        self.center = ((self.e['Tilemap'].dimensions[0] // 2) * tile_size, (self.e['Tilemap'].dimensions[1] // 2) * tile_size)
        center = self.center
        cam = self.e['Game'].camera
        self.e['Renderer'].renderf(pygame.draw.line, (100, 97, 139), (center[0] - cam[0], center[1] - (center[1] + 24) * axis_length - cam[1]), (center[0] - cam[0], center[1] + (center[1] + 24) * axis_length - cam[1]), z=0)
        self.e['Renderer'].renderf(pygame.draw.line, (100, 97, 139), (center[0] - (center[0] + 24) * axis_length - cam[0], center[1] - cam[1]), (center[0] + (center[0] + 24) * axis_length - cam[0], center[1] - cam[1]), z=0)
        self.e['Renderer'].renderf(pygame.draw.line, (205, 209, 201), (center[0] - cam[0], center[1] - (center[1] + 24) * axis_length_2 - cam[1]), (center[0] - cam[0], center[1] + (center[1] + 24) * axis_length_2 - cam[1]), z=0)
        self.e['Renderer'].renderf(pygame.draw.line, (205, 209, 201), (center[0] - (center[0] + 24) * axis_length_2 - cam[0], center[1] - cam[1]), (center[0] + (center[0] + 24) * axis_length_2 - cam[0], center[1] - cam[1]), z=0)

        w = self.e['Game'].display.get_width()
        scale = self.e['Tilemap'].dimensions[1] * 0.3 * tile_size
        scale = math.sin(self.e['Window'].time * 0.7) * scale * 0.2 + 0.5 * scale
        scale *= axis_length_2
        sine_plot = [((i - 1) * 4, math.sin(self.e['Window'].time * 2 + (i - 1 + cam[0] / 4) * 0.1) * scale + center[1] - cam[1]) for i in range(int(w / 4 + 3))]
        self.e['Renderer'].renderf(pygame.draw.lines, (67, 51, 87), False, sine_plot, z=-100)
