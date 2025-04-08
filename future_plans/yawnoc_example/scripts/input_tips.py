import pygame

from . import pygpen as pp

from .const import KEYBOARD_ICONS, OFFSET_N4

class InputTips(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

    def lookup_binding(self, binding, large=False, tiny=False):
        group = binding[0]
        key = binding[1]
        
        if group == 'mouse':
            size = 'big' if large else 'small'
            name = f'mouse_{key}_{size}'
            if name in self.e['Assets'].images['input_tips']:
                return self.e['Assets'].images['input_tips'][name]
        
        if key in KEYBOARD_ICONS:
            if key in KEYBOARD_ICONS:
                src, offset = KEYBOARD_ICONS[key]
                if tiny:
                    tiny_name = f'{src}_tiny'
                    if tiny_name in self.e['Assets'].images['input_tips']:
                        return self.e['Assets'].images['input_tips'][tiny_name]
                src_img = self.e['Assets'].images['input_tips'][src]
                if src == 'general':
                    return pp.gfx_util.clip(src_img, pygame.Rect(offset[0] * 9, offset[1] * 11, 7, 10))
                else:
                    return src_img
        
        return self.e['Assets'].images['input_tips']['unknown']
    
    def lookup_controller_binding(self, binding):
        name = f'controller_{binding}'
        if name in self.e['Assets'].images['input_tips']:
            return self.e['Assets'].images['input_tips'][name]
        return self.e['Assets'].images['input_tips']['unknown']
    
    @property
    def interact_icon(self):
        if self.e['Game'].controller_mode:
            return self.lookup_controller_binding('a')
        return self.lookup_binding(self.e['Input'].config['interact'])
    
    def render_icon(self, icon, pos, group='ui', z=0):
        silhouette = pygame.mask.from_surface(icon).to_surface(setcolor=(38, 27, 46), unsetcolor=(0, 0, 0, 0))
        for offset in OFFSET_N4:
            self.e['Renderer'].blit(silhouette, (pos[0] + offset[0], pos[1] + offset[1]), group=group, z=z - 0.0001)
        self.e['Renderer'].blit(icon, pos, group=group, z=z)