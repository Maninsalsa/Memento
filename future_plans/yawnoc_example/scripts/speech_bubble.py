import math

import pygame

from . import pygpen as pp

class SpeechBubble(pp.Element):
    def __init__(self, text):
        super().__init__()

        self.text = text
        self.progress = 0
        self.decaying = False

    def render(self, source):
        if self.text[0]:
            if self.decaying:
                self.progress = max(0, min(len(self.text) / 25 + 1 / 6, self.progress - self.e['Window'].dt * 5))
                if not self.progress:
                    self.text = None
            else:
                self.progress += self.e['Window'].dt
            if self.text:
                init_progress = min(self.progress * 6, 1)
                text_progress = max(0, self.progress - 1 / 6)
                chars_to_show = int(text_progress * 25)
                finished_for = text_progress - (len(self.text) / 25)
                if finished_for > 4:
                    self.decaying = True
                text = self.text[:chars_to_show]
                text_width = self.e['Text']['small_font'].width(text)
                src = (source[0] + 7, source[1] - 7)
                polygon_points = [
                    (6 * init_progress, -4 * init_progress),
                    (0, 0),
                    (5 * init_progress, -6 * init_progress),
                    (4 * init_progress, -9 * init_progress),
                    (6 * init_progress, -14 * init_progress),
                    (8 * init_progress + text_width * 0.5, -15 * init_progress),
                    (10 * init_progress + text_width, -14 * init_progress),
                    (12 * init_progress + text_width, -9 * init_progress),
                    (10 * init_progress + text_width, -4 * init_progress),
                    (8 * init_progress + text_width * 0.5, -3 * init_progress),
                    (6 * init_progress, -4 * init_progress),
                ]
                t = self.e['Window'].time
                polygon_points = [(p[0] + math.sin(i + t * 1.5) * 1.5, p[1] + math.cos(i + t * 1.2) * 1.5) for i, p in enumerate(polygon_points)]
                bubble_surf = pygame.Surface((text_width + 20, 20), pygame.SRCALPHA)
                pygame.draw.polygon(bubble_surf, (38, 27, 46), [(p[0], p[1] + bubble_surf.get_height()) for p in polygon_points])
                self.e['Text']['small_font'].renderz(text, (src[0] - self.e['Game'].camera[0] + 8, src[1] - self.e['Game'].camera[1] - 12), color=(254, 252, 211), z=101, group='ui')
                bubble_surf.set_alpha(150)
                self.e['Renderer'].blit(bubble_surf, (src[0] - self.e['Game'].camera[0], src[1] - self.e['Game'].camera[1] - bubble_surf.get_height()), z=100, group='ui')