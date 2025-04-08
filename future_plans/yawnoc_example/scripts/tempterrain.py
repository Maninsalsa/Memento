import math
import random

import pygame

from . import pygpen as pp

from .tilemap import Tile

class TempTerrain(pp.Element):
    def __init__(self, terrain_type, pos):
        super().__init__()

        self.type = terrain_type
        self.pos = tuple(pos)
        self.px_pos = ((self.pos[0] + 0.5) * self.e['Tilemap'].tile_size, (self.pos[1] + 0.5) * self.e['Tilemap'].tile_size)
    
        z_offset = -1
        if self.type == (1, 0):
            z_offset = -3
            self.e['Game'].player.play_from('sludge', self.px_pos, volume=0.7)
        self.tile = Tile(self.e['Tilemap'], 'tempterrain', self.pos, wall=True, variant=self.type, z_offset=z_offset)

        valid = True
        if 'entities' in self.e['EntityGroups'].groups:
            for temp_terrain in self.e['EntityGroups'].groups['entities']:
                if type(temp_terrain) == TempTerrain:
                    if temp_terrain.pos == self.pos:
                        valid = False

        if valid:
            self.rect = pygame.Rect(self.pos[0] * self.e['Tilemap'].tile_size, self.pos[1] * self.e['Tilemap'].tile_size, self.e['Tilemap'].tile_size, self.e['Tilemap'].tile_size)
            if (not self.rect.colliderect(self.e['Game'].player.rect)) and self.e['Tilemap'].is_open_space(self.pos) and (self.pos not in self.e['Machines'].machine_map):
                if self.type == (0, 0):
                    self.e['Tilemap'].solids[self.pos] = self.tile

                self.poof()

                self.life = 15
            else:
                self.life = 0
        else:
            self.life = 0

        self.y_offset = self.e['Assets'].spritesheets[self.tile.type]['assets'][self.tile.variant].get_height() - self.e['Tilemap'].tile_size

        self.timer = 0

    def poof(self):
        spark_colors = [(193, 159, 113), (149, 86, 68), (106, 51, 60)]
        for i in range(20):
            self.e['EntityGroups'].add(pp.vfx.Spark(self.px_pos, random.random() * math.pi * 2, size=(random.randint(3, 6), random.randint(1, 2)), speed=random.random() * 70 + 70, decay=random.random() * 3 + 0.5, color=random.choice(spark_colors), z=5981), 'vfx')
    
    def update(self, dt):
        self.life -= dt
        
        self.timer += dt
        if (self.type == (1, 0)) and (self.timer > 0.7):
            self.timer -= 0.7
            if self.pos in self.e['Machines'].machine_map:
                machine = self.e['Machines'].machine_map[self.pos]
                machine.damage(1.3 * (self.e['State'].upgrade_stat('hostile_environment') + 1))
                for i in range(5):
                    color = random.choice([(100, 97, 139), (121, 132, 157), (163, 179, 182), (37, 91, 107), (37, 91, 107)])
                    p = pp.vfx.Particle((machine.center[0] + random.random() * 8 - 4, machine.center[1] + random.random() * 5 - 12), 'basep', (0, -8 + random.random() * 4), decay_rate=0.02, advance=0.3 + 0.4 * random.random(), colors={(255, 255, 255): color}, z=self.pos[1] + 0.52, behavior='smoke')
                    self.e['EntityGroups'].add(p, 'particles')

        if self.life <= 0:
            if self.pos in self.e['Tilemap'].solids:
                self.poof()
                del self.e['Tilemap'].solids[self.pos]
            return True
    
    def renderz(self, offset=(0, 0), group='default'):
        if self.life:
            self.tile.render(offset=(offset[0], offset[1] + self.y_offset))
