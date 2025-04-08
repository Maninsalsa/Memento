import pygame

from . import pygpen as pp

from .bullet import Bullet

class Laser(pp.Element):
    def __init__(self, source, angle, no_dot=False, rot_vel=0):
        super().__init__()

        self.type = 'laser'

        self.source = list(source)
        self.angle = angle

        self.compute_length()

        self.base_fire_speed = 350
        self.bullet_count = 5
        self.bullet_speed_variance = 50
        
        self.life = 2
        self.time = 0

        self.rot_vel = rot_vel

        self.no_dot = no_dot

    def compute_length(self):
        self.end = self.source.copy()
        for i in range(1000):
            self.end = pp.game_math.advance(self.end, self.angle, 4)
            if self.e['Tilemap'].solid_check(self.end, include_gaps=False):
                break

        self.range = pp.game_math.distance(self.source, self.end)

    @property
    def fastest_bullet(self):
        return self.base_fire_speed + self.bullet_count * self.bullet_speed_variance

    def update(self, dt):
        if self.life >= 0 > self.life - dt:
            for i in range(self.bullet_count):
                bullet = Bullet('red', self.source, self.angle)
                bullet.speed = self.base_fire_speed + i * self.bullet_speed_variance
                self.e['EntityGroups'].add(bullet, 'entities')
            self.e['Game'].player.play_from('shoot', self.source, volume=0.3)

        if self.life > 0.5:
            self.angle += self.rot_vel * dt
            if self.rot_vel:
                self.compute_length()

        self.life -= dt
        self.time += dt

        return self.life < -self.range / self.fastest_bullet
    
    def renderz(self, offset=(0, 0), group='default'):
        start = pp.game_math.advance(self.source.copy(), self.angle, 6)
        length = pp.game_math.distance(start, self.end) * min(self.time * 3, 1)
        if self.life < 0:
            start = pp.game_math.advance(start, self.angle, -self.life * self.fastest_bullet)
        display_start = (start[0] - offset[0], start[1] - offset[1])
        if self.life >= 0:
            if not self.no_dot:
                for offset_2 in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                    self.e['Renderer'].renderf(pygame.draw.circle, (254, 252, 211), (display_start[0] + offset_2[0], display_start[1] + offset_2[1]), 4, group=group, z=5987.9999)
                self.e['Renderer'].renderf(pygame.draw.circle, (191, 60, 96), display_start, 4, group=group, z=5988)
        self.e['Renderer'].renderf(pygame.draw.line, (191, 60, 96), display_start, pp.game_math.advance(list(display_start), self.angle, length), group=group, z=-3)