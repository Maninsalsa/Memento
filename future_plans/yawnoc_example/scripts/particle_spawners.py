import math

import random

from .pygpen.vfx import Particle, particle_behavior, particle_init

@particle_init('smoke')
def idle_init(self):
    pass

@particle_behavior('smoke')
def smoke_behave(self, dt):
    self.pos[0] += math.sin(self.e['Window'].time * 1.2 + self.unique) * dt * 5

def update_spawner(spawner_type, source, tilemap):
    e = tilemap.e
    dt = e['Window'].dt

    if spawner_type == 'fire':
        if random.random() < dt * 3:
            p = Particle((source[0] + random.random() * 6 - 3, source[1] + random.random() * 2 - 1), random.choice(['flamep1', 'flamep2']), (0, 0), advance=0, decay_rate=0.8, z=source[1] / tilemap.tile_size + 10)
            e['EntityGroups'].add(p, 'particles')
    
    if spawner_type == 'smoke':
        if random.random() < dt * 3:
            color = random.choice([(100, 97, 139), (121, 132, 157), (163, 179, 182)])
            p = Particle(source, 'basep', (0, -6), decay_rate=0.02, advance=0.3 + 0.4 * random.random(), colors={(255, 255, 255): color}, z=source[1] / tilemap.tile_size + 10, behavior='smoke')
            e['EntityGroups'].add(p, 'particles')