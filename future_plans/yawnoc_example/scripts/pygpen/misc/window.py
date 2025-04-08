import os
import time

import pygame

from ..utils.elements import ElementSingleton
from ..mgl.mgl import MGL

from ...crash_report import CRASH_REPORTER

class Window(ElementSingleton):
    def __init__(self, dimensions=(640, 480), caption='pygpen window', flags=0, fps_cap=60, dt_cap=1, opengl=False, frag_path=None):
        super().__init__()
        self.opengl = opengl
        self.frag_path = frag_path
        self.dimensions = dimensions
        self.flags = flags
        if self.opengl:
            self.flags = self.flags | pygame.DOUBLEBUF | pygame.OPENGL
        self.fps_cap = fps_cap
        self.dt_cap = dt_cap
        self.background_color = (0, 0, 0)
        self.time = time.time()
        self.start_time = time.time()
        self.frames = 0
        self.frame_log = []
        self.native_resolution = None
        
        pygame.display.set_caption(caption)
        self.reload_display(self.dimensions, ignore_mgl=True)
        self.clock = pygame.time.Clock()
        
        self.last_frame = time.time()
        self.dt = 0.1
        
        self.render_object = None
        if self.opengl:
            MGL()
            if not self.frag_path:
                self.render_object = self.e['MGL'].default_ro()
            else:
                self.render_object = self.e['MGL'].render_object(frag_path)

    @property
    def fps(self):
        return len(self.frame_log) / sum(self.frame_log)
        
    @property
    def runtime(self):
        return self.time - self.start_time
    
    @property
    def border_discard(self):
        ratio = self.dimensions[0] / self.dimensions[1]
        if ratio > 16 / 9:
            proper_width = self.dimensions[1] * 16 / 9
            return (1 - proper_width / self.dimensions[0], 0)
        elif ratio < 16 / 9:
            proper_height = self.dimensions[0] / 16 * 9
            return (0, 1 - proper_height / self.dimensions[1])
        else:
            return (0, 0)
    
    def reload_display(self, size, ignore_mgl=False):
        try:
            fullscreen = self.e['Settings'].fullscreen
        except Exception:
            fullscreen = False

        self.fullscreen_flag = pygame.FULLSCREEN if fullscreen else 0

        CRASH_REPORTER.state['display'] = {
            'loading': True,
            'size': size,
            'fullscreen': fullscreen,
            'flags': self.flags,
        }

        # if starting up, use pygame.display.Info() size it contains the accurate size
        if fullscreen and ignore_mgl:
            size = (pygame.display.Info().current_w, pygame.display.Info().current_h)

        if not self.native_resolution:
            self.native_resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        elif not fullscreen:
            # this is not the first load, so make sure that the window isn't stuck to the top left
            os.environ['SDL_VIDEO_CENTERED'] = '0'

        # native resolution requested
        if not size:
            size = self.native_resolution

        CRASH_REPORTER.state['display']['size'] = size

        self.screen = pygame.display.set_mode(size, self.flags | self.fullscreen_flag)
        if not ignore_mgl:
            self.e['MGL'].ctx.viewport = 0, 0, size[0], size[1]
        if fullscreen:
            self.dimensions = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        else:
            self.dimensions = tuple(size)

        CRASH_REPORTER.state['display']['loading'] = False
    
    def cycle(self, uniforms={}):
        if self.render_object:
            if self.render_object.default and ('surface' not in uniforms):
                uniforms['surface'] = self.screen
            self.render_object.render(uniforms=uniforms)
        pygame.display.flip()
        self.clock.tick(self.fps_cap)
        self.dt = max(0.0001, min(time.time() - self.last_frame, self.dt_cap))
        self.frame_log.append(self.dt)
        self.frame_log = self.frame_log[-60:]
        self.last_frame = time.time()
        self.screen.fill(self.background_color)
        if self.render_object:
            self.e['MGL'].ctx.clear(*[self.background_color[i] / 255 for i in range(3)], 1.0)
        self.e['Input'].update()
        self.time = time.time()
        self.frames += 1
        