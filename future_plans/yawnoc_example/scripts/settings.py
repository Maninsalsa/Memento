import time
import os
import socket
import platform

import pygame

from scripts import pygpen as pp

from .util import CONTROLLER_MAPPING_SWAPPED, CONTROLLER_MAPPING
from .const import DEFAULT_SAVE, SETTINGS

DEFAULT_SETTINGS = {
    'fps_cap': '165',
    'master_volume': '100%',
    'sfx_volume': '100%',
    'music_volume': '100%',
    'fullscreen': 'disabled',
    'aim_assist': '100%',
    'windowed_resolution': 'native',
    'outline': 'enabled',
    'show_fps': 'disabled',
    'swap_trigger_bumper': 'disabled',
    'pink_player': 'disabled',
    'saturation': '100%',
    'screenshake': 'enabled',
    'crt_effect': '100%',
    'camera_slack': 'enabled',
    'camera_mouse_influence': '50%',
    'machine_outline': 'disabled',
    'bullet_outline': 'disabled',
    'grass': 'enabled',
    'trees': 'breezy',
    'ability_cooldowns': 'hud',
}

class Settings(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        if not os.path.isdir('save'):
            os.mkdir('save')

        if not os.path.isdir('settings'):
            os.mkdir('settings')
        
        if not os.path.exists('save/save.json'):
            pp.utils.io.write_json('save/save.json', DEFAULT_SAVE)

        max_display_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        for option in list(SETTINGS['windowed_resolution']['options']):
            if 'x' in option:
                if int(option.split('x')[0]) > max_display_size[0]:
                    SETTINGS['windowed_resolution']['options'].remove(option)
                    print('removed oversized resolution option:', option)
                elif int(option.split('x')[1]) > max_display_size[1]:
                    SETTINGS['windowed_resolution']['options'].remove(option)
                    print('removed oversized resolution option:', option)
                    
        try:
            self.settings_save = pp.utils.io.read_json('settings/settings.json')
            for field in DEFAULT_SETTINGS:
                if field not in self.settings_save:
                    self.settings_save[field] = DEFAULT_SETTINGS[field]
                elif self.settings_save[field] not in SETTINGS[field]['options']:
                    self.settings_save[field] = DEFAULT_SETTINGS[field]
        except FileNotFoundError:
            initial_resolution = 'native'
            # setting the windowed resolution to the display resolution doesn't emulate fullscreen on all linux distros
            # however, defaulting to native on steamdeck is ideal
            if (platform.system().lower() == 'linux') and (not self.steamdeck):
                initial_resolution = '1152x648'

            new_settings = DEFAULT_SETTINGS.copy()
            new_settings['windowed_resolution'] = initial_resolution

            self.settings_save = new_settings
            self.save()

    def save(self):
        pp.utils.io.write_json('settings/settings.json', self.settings_save)

    def setting(self, field):
        return self.settings_save[field] if field in self.settings_save else None
    
    @property
    def steamdeck(self):
        return socket.gethostname() == 'steamdeck'
    
    @property
    def sfx_volume(self):
        return int(self.settings_save['sfx_volume'][:-1]) * 0.01 * int(self.settings_save['master_volume'][:-1]) * 0.01

    @property
    def music_volume(self):
        return int(self.settings_save['music_volume'][:-1]) * 0.01 * int(self.settings_save['master_volume'][:-1]) * 0.01
    
    @property
    def saturation(self):
        return int(self.settings_save['saturation'][:-1]) * 0.01
    
    @property
    def crt_effect(self):
        return int(self.settings_save['crt_effect'][:-1]) * 0.01

    @property
    def grass_visible(self):
        return self.settings_save['grass'] != 'disabled'
    
    @property
    def grass_breeze(self):
        return self.settings_save['grass'] == 'enabled'
    
    @property
    def tree_breeze(self):
        return self.settings_save['trees'] != 'no breeze'
    
    @property
    def fullscreen(self):
        return self.settings_save['fullscreen'] == 'enabled'

    @property
    def camera_slack(self):
        return self.settings_save['camera_slack'] == 'enabled'
    
    @property
    def machine_outline(self):
        return self.settings_save['machine_outline'] == 'enabled'

    @property
    def bullet_outline(self):
        return self.settings_save['bullet_outline'] == 'enabled'
    
    @property
    def camera_mouse_influence(self):
        return int(self.settings_save['camera_mouse_influence'][:-1]) * 0.01
    
    @property
    def screenshake(self):
        return self.settings_save['screenshake'] == 'enabled'
    
    @property
    def player_cooldowns(self):
        return self.settings_save['ability_cooldowns'] == 'player & hud'
    
    @property
    def aim_assist(self):
        return int(self.settings_save['aim_assist'][:-1]) * 0.01
    
    @property
    def resolution(self):
        try:
            return tuple(int(v) for v in self.settings_save['windowed_resolution'].split('x'))
        except ValueError:
            return None
    
    def update(self, field, value, save=True):
        self.settings_save[field] = value
        if save:
            self.save()

        if field == 'swap_trigger_bumper':
            self.e['Controllers'].update_mappings(CONTROLLER_MAPPING_SWAPPED if value == 'enabled' else CONTROLLER_MAPPING)
        if field == 'fps_cap':
            try:
                self.e['Window'].fps_cap = int(value)
            except ValueError:
                self.e['Window'].fps_cap = 9999
        if field in {'sfx_volume', 'master_volume'}:
            self.e['Sounds'].sounds['ambience'].set_volume(self.sfx_volume * 0.6)
        if field == 'windowed_resolution':
            self.e['Window'].reload_display(self.resolution)
        if field == 'fullscreen':
            size = self.e['Window'].dimensions
            if self.fullscreen:
                size = (0, 0)
            else:
                size = self.resolution
            self.e['Window'].reload_display(size)

            # sometimes I just get a black screen from going straigh to fullscreen once
            # double toggling seems to fix this issue
            if self.fullscreen:
                self.settings_save['fullscreen'] = 'disabled'
                self.e['Window'].reload_display(size)
                self.settings_save['fullscreen'] = 'enabled'
                self.e['Window'].reload_display(size)
            