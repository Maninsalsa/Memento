import random

import pygame

from ..utils.gfx import smooth_approach
from ..utils.elements import Element

class Camera(Element):
    def __init__(self, size, pos=(0, 0), slowness=1, tilemap_lock=None):
        super().__init__()
        self.size = size
        self.slowness = slowness
        self.pos = list(pos)
        self.base_pos = self.pos.copy()
        self.int_pos = (int(self.pos[0]), int(self.pos[1]))
        self.target_entity = None
        self.target_pos = None
        self.tilemap_lock = tilemap_lock

        self.rect_exp = pygame.Rect(self.int_pos[0] - 5, self.int_pos[1] - 5, self.size[0] + 10, self.size[1] + 10)

        self.screenshake = 0

    @property
    def rect(self):
        return pygame.Rect(*self.int_pos, *self.size)
    
    @property
    def target(self):
        if self.target_entity:
            if self.e['Game'].controller_mode:
                stick_offset = self.e['Controllers'].read_stick('aim_x', 'aim_y')
                world_mpos = pygame.Vector2(self.e['Game'].player.center[0] + stick_offset[0] * 150, self.e['Game'].player.center[1] + stick_offset[1] * 150)
            else:
                world_mpos = pygame.Vector2(self.e['Game'].mpos[0] + self.pos[0], self.e['Game'].mpos[1] + self.pos[1])
            mouse_effect = 1.0 - min(self.e['Transition'].level_end * 2, 1.0)
            if self.e['State'].title:
                mouse_effect = 0.1
            if self.e['State'].left_inv_offset:
                mouse_effect = max(0, 1.0 - self.e['State'].left_inv_offset / 200)
            mouse_effect = min(mouse_effect * self.e['Settings'].camera_mouse_influence, (1 - self.e['Transition'].progress) * self.e['Settings'].camera_mouse_influence)
            return ((world_mpos - pygame.Vector2(self.size) * 0.5) * mouse_effect + (self.target_entity.center[0] - self.size[0] // 2, self.target_entity.center[1] - self.size[1] // 2)) / (1 + mouse_effect)
        elif self.target_pos:
            return (self.target_pos[0] - self.size[0] // 2, self.target_pos[0] - self.size[1] // 2)
    
    def set_target(self, target):
        if hasattr(target, 'center'):
            self.target_entity = target
            self.target_pos = None
        elif target:
            self.target_pos = tuple(target)
            self.target_entity = None
        else:
            self.target_pos = None
            self.target_entity = None
            
    def __iter__(self):
        for v in self.int_pos:
            yield v
        
    def __getitem__(self, item):
        return self.int_pos[item]
    
    def move(self, movement):
        self.base_pos[0] += movement[0]
        self.base_pos[1] += movement[1]
    
    def update(self):
        dt = self.e['Window'].dt

        self.screenshake = max(0, self.screenshake - dt)

        target = self.target
        if target:
            if self.e['Settings'].camera_slack:
                self.base_pos[0] = smooth_approach(self.base_pos[0], target[0], slowness=self.slowness)
                self.base_pos[1] = smooth_approach(self.base_pos[1], target[1], slowness=self.slowness)
            else:
                self.base_pos = list(self.target)
            if self.tilemap_lock:
                self.base_pos[0] = max(0, min(self.tilemap_lock.dimensions[0] * self.tilemap_lock.tile_size - self.size[0], self.base_pos[0]))
                self.base_pos[1] = max(0, min(self.tilemap_lock.dimensions[1] * self.tilemap_lock.tile_size - self.size[1], self.base_pos[1]))

        self.pos = self.base_pos.copy()
        if self.screenshake:
            self.pos = [self.base_pos[0] + (random.random() - 0.5) * 4, self.base_pos[1] + (random.random() - 0.5) * 6]

        self.int_pos = (int(self.pos[0]), int(self.pos[1]))

        self.rect_exp = pygame.Rect(self.int_pos[0] - 5, self.int_pos[1] - 5, self.size[0] + 10, self.size[1] + 10)
    
    