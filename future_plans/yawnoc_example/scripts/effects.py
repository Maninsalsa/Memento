import math
import random

from . import pygpen as pp

class EntityEffects(pp.Element):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.freeze = 0
        self.confusion = 0
        self.flame = [0, 0]

        self.z_offset = 0

    def has_effect(self, effect_id):
        if effect_id == 'flame':
            return bool(self.flame[0])
        if effect_id == 'freeze':
            return bool(self.freeze)
        if effect_id == 'confusion':
            return bool(self.confusion)
        
    def apply_effect(self, effect_id, duration):
        if effect_id == 'flame':
            self.flame[0] = duration
            self.e['Game'].player.play_from('ignite', self.parent.center, volume=0.5)
        if effect_id == 'freeze':
            self.freeze = duration
        if effect_id == 'confusion':
            self.confusion = max(self.confusion, duration)

    def copy(self, new_parent):
        effects = EntityEffects(new_parent)
        effects.freeze = self.freeze
        effects.confusion = self.confusion
        effects.flame = self.flame.copy()

    @property
    def status_affected(self):
        return self.flame[0] or self.freeze or self.confusion
    
    @property
    def frozen(self):
        return self.e['State'].effect_active('freeze') or self.freeze
    
    def update(self):
        ts = self.e['Tilemap'].tile_size
        
        if self.flame[0]:
            self.flame[0] = max(0, self.flame[0] - self.e['Window'].dt)
            self.flame[1] += self.e['Window'].dt
            if self.flame[1] > 0.8:
                self.flame[1] -= 0.8
                self.parent.damage(0.5 * (self.e['State'].upgrade_stat('hostile_environment') + 1), alternate_source=True)

            if random.random() < self.e['Window'].dt * 6:
                p = pp.vfx.Particle((self.parent.center[0] + random.random() * 10 - 5, self.parent.center[1] + random.random() * 10 - 7), random.choice(['flamep1', 'flamep2']), (0, 0), advance=0, decay_rate=0.8, z=self.parent.center[1] / ts + 0.51 + self.z_offset)
                self.e['EntityGroups'].add(p, 'particles')
            if random.random() < self.e['Window'].dt * 4:
                color = random.choice([(100, 97, 139), (121, 132, 157), (163, 179, 182)])
                p = pp.vfx.Particle((self.parent.center[0] + random.random() * 10 - 5, self.parent.center[1] + random.random() * 5 - 8), 'basep', (0, -6), decay_rate=0.02, advance=0.3 + 0.4 * random.random(), colors={(255, 255, 255): color}, z=self.parent.center[1] / ts + 0.52 + self.z_offset, behavior='smoke')
                self.e['EntityGroups'].add(p, 'particles')

        self.freeze = max(0, self.freeze - self.e['Window'].dt)
        self.confusion = max(0, self.confusion - self.e['Window'].dt)

    def render(self, offset=(0, 0)):
        ts = self.e['Tilemap'].tile_size

        if self.frozen:
            ice_img = self.e['Assets'].images['misc']['ice']
            self.e['Renderer'].blit(ice_img, (self.parent.center[0] - offset[0] - ice_img.get_width() / 2, self.parent.center[1] - offset[1] - ice_img.get_height() / 2 - 5), z=self.parent.center[1] / ts + 0.49 + self.z_offset)

        if self.confusion:
            for i in range(3):
                angle = i * math.pi * 2 / 3 + self.e['Window'].time
                self.e['Renderer'].blit(self.e['Assets'].images['misc']['confusion_star'], (self.parent.center[0] - offset[0] + math.cos(angle) * 6.5 - 2, self.parent.center[1] - offset[1] - 10 + math.sin(angle) * 6.5), z=self.parent.center[1] / ts + 0.5 + self.z_offset)

    def update_render(self, offset=(0, 0)):
        self.update()
        self.render(offset=offset)
            