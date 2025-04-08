import pygame

from . import pygpen as pp

AUTOMATA_SYSTEMS = ['cgol', 'highlife', 'brain', 'lowdeath', 'blobell', 'blursed']

class Automata(pp.ElementSingleton):
    def __init__(self, dimensions=(100, 100)):
        super().__init__()

        self.fbo = None
        self.depth_tex = None
        self.color_tex = None

        self.update_dimensions(dimensions)

        self.current_automata = 'cgol'

        self.ros = {system: self.e['MGL'].render_object(f'data/shaders/{system}.frag') for system in AUTOMATA_SYSTEMS}

        self.uniforms = {'spawner_spawn_id': 0}

    @property
    def ro(self):
        return self.ros[self.current_automata]

    def clear(self):
        if self.fbo:
            self.depth_tex.release()
            self.color_tex.release()
            self.fbo.release()
        self.depth_tex = self.e['MGL'].ctx.depth_texture(self.dimensions)
        self.color_tex = self.e['MGL'].ctx.texture(self.dimensions, 4)
        self.fbo = self.e['MGL'].ctx.framebuffer(color_attachments=[self.color_tex], depth_attachment=self.depth_tex)
        if self.dimensions == self.e['Tilemap'].dimensions:
            self.automata_map = self.e['Tilemap'].wall_map.copy()
        else:
            self.automata_map = pygame.Surface(self.dimensions, pygame.SRCALPHA)


    def update_dimensions(self, dimensions):
        self.dimensions = dimensions
        self.clear()

    def step(self):
        automata_tex = self.e['MGL'].pg2tx(self.automata_map, swizzle=True)
        uniforms = self.uniforms.copy()
        uniforms['surface'] = automata_tex
        self.ro.render(dest=self.fbo, uniforms=uniforms)
        self.automata_map = self.e['MGL'].tx2pg(self.color_tex)
        automata_tex.release()