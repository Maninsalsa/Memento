import pygame

from . import pygpen as pp
from .pygpen import Entity

class PhysicsRect(pp.Element):
    def __init__(self, rect):
        super().__init__()

        self.pos = list(rect.topleft)
        self.size = rect.size

    @property
    def rect(self):
        return pygame.Rect(*self.pos, *self.size)

    def physics_update(self, movement):
        neighbors = self.e['Game'].tilemap.solids_around(self.rect.center)

        self.pos[0] += movement[0]
        init_rect = self.rect
        rect = self.rect
        for tile in neighbors:
            if tile.rect.colliderect(self.rect):
                if movement[0] > 0:
                    rect.right = tile.rect.left
                if movement[0] < 0:
                    rect.left = tile.rect.right
        if init_rect.x != rect.x:
            self.pos[0] = rect.x

        self.pos[1] += movement[1]
        init_rect = self.rect
        rect = self.rect
        for tile in neighbors:
            if tile.rect.colliderect(self.rect):
                if movement[1] > 0:
                    rect.bottom = tile.rect.top
                if movement[1] < 0:
                    rect.top = tile.rect.bottom
        if init_rect.y != rect.y:
            self.pos[1] = rect.y

class PhysicsEntity(Entity):
    def physics_update(self, movement):
        neighbors = self.e['Game'].tilemap.solids_around(self.center)

        self.pos[0] += movement[0]
        init_rect = self.rect
        rect = self.rect
        for tile in neighbors:
            if tile.rect.colliderect(self.rect):
                if movement[0] > 0:
                    rect.right = tile.rect.left
                if movement[0] < 0:
                    rect.left = tile.rect.right
        if init_rect.x != rect.x:
            self.pos[0] = rect.x

        self.pos[1] += movement[1]
        init_rect = self.rect
        rect = self.rect
        for tile in neighbors:
            if tile.rect.colliderect(self.rect):
                if movement[1] > 0:
                    rect.bottom = tile.rect.top
                if movement[1] < 0:
                    rect.top = tile.rect.bottom
        if init_rect.y != rect.y:
            self.pos[1] = rect.y
        

