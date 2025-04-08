import math
import random

from . import pygpen as pp

from .bullet import Bullet

class Drop(pp.Element):
    def __init__(self, drop_type, pos):
        super().__init__()

        self.type = drop_type

        if (self.type == 'scrap') and (self.e['State'].upgrade_stat('potato_farmer')) and (random.random() < 0.2):
            self.e['EntityGroups'].add(Drop('potato', pos), 'entities')

        self.pos = [pos[0], pos[1], 0]

        self.angle = random.random() * math.pi * 2
        self.speed = random.random() * 70 + 40
        self.v_speed = random.random() * 120 + 40

        self.life = 10

        self.following = False

    def update(self, dt):
        self.pos[0] += math.cos(self.angle) * self.speed * dt
        self.pos[1] += math.sin(self.angle) * self.speed * dt
        self.pos[2] += self.v_speed * dt

        self.speed = pp.utils.game_math.normalize(self.speed, 100 * dt)
        self.v_speed -= 200 * dt

        self.life = max(0, self.life - dt)
        if not self.life:
            return True
        
        if self.e['Machines'].no_enemy_dur:
            self.following = True

        if abs(self.v_speed) < 20:
            dis = pp.utils.game_math.distance(self.pos[:2], self.e['Game'].player.center)
            follow_range = 64 * (1 + self.e['State'].upgrade_stat('magnet'))
            if (dis < follow_range) or self.following:
                self.following = True
                self.angle = math.atan2(self.e['Game'].player.center[1] - self.pos[1], self.e['Game'].player.center[0] - self.pos[0])
                self.speed += 500 * dt
                if dis < 6:
                    for i in range(8):
                        self.e['EntityGroups'].add(pp.vfx.Spark(self.pos[:2], random.random() * math.pi * 2, size=(random.randint(3, 5), 1), speed=random.random() * 60 + 60, decay=random.random() * 4 + 2, color=(254, 252, 211), z=0), 'vfx')
                    if self.type == 'scrap':
                        self.e['State'].scrap += 1
                        self.e['HUD'].scrap_spin = 360
                        self.e['Sounds'].play('jingle', volume=0.2)
                        if self.e['State'].upgrade_stat('cash_overflow'):
                            self.e['EntityGroups'].add(Bullet('blue', self.pos[:2], random.random() * math.pi * 2, advance=4, base_range=150, damage=2, speed=110), 'entities')
                            self.e['Sounds'].play('shoot', volume=0.15)
                    else:
                        self.e['State'].add_potato()
                    return True

        if self.pos[2] < 0:
            if abs(self.v_speed) > 20:
                self.pos[2] *= -1
                self.v_speed *= -0.5
            else:
                self.pos[2] = 0
                self.v_speed = 0

    def renderz(self, offset=(0, 0), group='default'):
        if (self.life > 2) or (random.random() > 0.5):
            img = self.e['Assets'].images['drops'][self.type]
            shadow_img = self.e['Assets'].images['misc']['shadow_small']
            self.e['Renderer'].blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - self.pos[2] - offset[1] - img.get_height() // 2), group=group, z=self.pos[1] / self.e['Tilemap'].tile_size)
            self.e['Renderer'].blit(shadow_img, (self.pos[0] - offset[0] - shadow_img.get_width() // 2, self.pos[1] - offset[1] - shadow_img.get_height() // 2 + img.get_height() // 2), group=group, z=self.pos[1] / self.e['Tilemap'].tile_size)
