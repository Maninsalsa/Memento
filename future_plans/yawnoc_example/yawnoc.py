from scripts.crash_report import CRASH_REPORTER

try:
    import sys
    import time
    import math

    import pygame

    import scripts.pygpen as pp
    from scripts.player import Player
    from scripts.frenemy import Frenemy
    from scripts.tilemap import Tilemap
    from scripts.machines import Machines
    from scripts.minimap import Minimap
    from scripts.state import State
    from scripts.bullet import Bullet
    from scripts.highlife_map import HighlifeMap
    from scripts.transition import Transition
    from scripts.menus import Menus
    from scripts.hud import HUD
    from scripts.snow import Snow
    from scripts.settings import Settings
    from scripts.music import Music
    from scripts.aim_assist import AimAssist
    from scripts.presence import Presence
    from scripts.steamworks import Steamworks
    from scripts.input_tips import InputTips
    from scripts.blood_bg import BloodBG
    from scripts.visibility_markers import VisibilityMarkers
    from scripts.setup import generate_shadow_anims, prep_assets
    from scripts.util import CONTROLLER_MAPPING, CONTROLLER_MAPPING_SWAPPED

    # force packaging to recognize glcontext
    import glcontext

    class Game(pp.PygpenGame):
        def load(self):
            base_resolution = (384, 216)

            # moved this out of the Window object so that it can be done before settings are loaded
            pygame.mixer.pre_init(channels=2, allowedchanges=pygame.AUDIO_ALLOW_FREQUENCY_CHANGE)
            pygame.init()

            self.settings = Settings()

            try:
                fps_cap = int(self.settings.setting('fps_cap'))
            except ValueError:
                fps_cap = 9999

            pp.init(
                self.settings.resolution,
                entity_path='data/images/entities',
                sounds_path='data/sfx',
                spritesheet_path='data/images/spritesheets',
                caption='Yawnoc',
                input_path='data/config/key_mappings.json',
                font_path='data/fonts',
                fps_cap=fps_cap,
                opengl=True,
                frag_path='data/shaders/main.frag',
            )

            self.e['Input'].enable_controllers(CONTROLLER_MAPPING_SWAPPED if self.e['Settings'].setting('swap_trigger_bumper') == 'enabled' else CONTROLLER_MAPPING, 'data')

            pygame.mouse.set_visible(False)

            self.display = pygame.Surface(base_resolution, pygame.SRCALPHA)
            self.hud_surf = self.display.copy()

            self.gm = pp.vfx.GrassManager('data/images/grass', tile_size=12, place_range=[0, 1], shade_amount=60)
            self.gm.enable_ground_shadows(shadow_radius=4, shadow_color=(38, 27, 46))

            self.e['Renderer'].set_groups(['default', 'ui'])

            self.player = None

            self.state = State()

            self.player = Player('player', (300, 300))
            self.e['EntityGroups'].add(self.player, 'entities')

            self.e['Assets'].enable('foliage')
            self.e['Assets'].load_folder('data/images/tiles', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/weapons', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/machines', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/patterns')
            self.e['Assets'].load_folder('data/images/misc', colorkey=(0, 0, 0), alpha=True)
            self.e['Assets'].load_folder('data/images/rigs', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/drops', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/upgrades', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/debris', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/decor', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/portraits', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/partner_icons', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/projectiles', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/leaf', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/difficulties', colorkey=(0, 0, 0))
            self.e['Assets'].load_folder('data/images/input_tips', colorkey=(0, 0, 0))

            pygame.display.set_icon(self.e['Assets'].images['misc']['icon'])

            self.noise_tex = self.e['MGL'].pg2tx(self.e['Assets'].images['misc']['noise'])
            self.noise_tex.repeat_x = True
            self.noise_tex.repeat_y = True
            self.static_noise_tex = self.e['MGL'].pg2tx(self.e['Assets'].images['misc']['static_noise'])
            self.static_noise_tex.repeat_x = True
            self.static_noise_tex.repeat_y = True
            self.crt_filter_tex = self.e['MGL'].pg2tx(self.e['Assets'].images['misc']['crt_filter'])
            self.crt_filter_tex.repeat_x = True
            self.crt_filter_tex.repeat_y = True

            self.cracks = [self.e['MGL'].pg2tx(self.e['Assets'].images['misc'][f'crack_{i}']) for i in range(3)]
            for crack in self.cracks:
                crack.repeat_x = True
                crack.repeat_y = True
            self.crack_img = self.cracks[0]

            prep_assets(self.e['Assets'])

            self.menus = Menus()
            self.visibility_markers = VisibilityMarkers()
            self.tilemap = Tilemap()
            self.hlmap = HighlifeMap()

            self.music = Music()
            self.aim_assist = AimAssist()

            self.camera = pp.Camera(base_resolution, slowness=0.2, tilemap_lock=self.tilemap)
            self.camera.set_target(self.player)

            self.machines = Machines()
            self.minimap = Minimap()

            self.transition = Transition()
            self.hud = HUD()
            self.input_tips = InputTips()
            self.snow = Snow()
            self.bloodbg = BloodBG()

            self.presence = Presence()
            self.steamworks = Steamworks()

            self.mpos = (0, 0)

            self.freeze_stack = []

            self.controller_mode = False
            self.controller_aim_offset = [30, 0]

            generate_shadow_anims(self)

            self.e['Sounds'].play('ambience', times=-1, volume=self.e['Settings'].sfx_volume * 0.6)

            self.state.load_title()

        def restart(self):
            self.player.pos = [300, 300]
            for entity in self.e['EntityGroups'].groups['entities']:
                if type(entity) == Bullet:
                    entity.life = 0
            self.state.reset()
            self.state.load_title()
            self.machines.reset(soft=True)
            self.player.max_health = 5.2
            self.player.health = self.player.max_health
            self.e['Transition'].direction = -1
            self.e['PauseMenu'].death_consumed = False
        
        def restart_retry(self):
            self.restart()

            self.e['Input'].consume('shoot')
            self.e['Controllers'].consume('interact')

            self.e['Menus'].submenu = 'weapon_select'
            self.e['Menus'].next_menu = None

        def handle_controller_switch(self):
            if self.controller_mode:
                if any(self.e['Mouse'].movement):
                    self.controller_mode = False
            else:
                if any([self.e['Controllers'].pressed(key) or self.e['Controllers'].pressed_neg(key) for key in ['move_x', 'move_y', 'aim_x', 'aim_y']]):
                    self.controller_mode = True
                if any([self.e['Controllers'].pressed(key) for key in ['menu_right', 'menu_left', 'menu_up', 'menu_down']]):
                    self.controller_mode = True

        def update(self):
            self.hud_surf.fill((0, 0, 0, 0))
            self.display.fill((0, 0, 0, 0))

            self.e['Sounds'].update()

            self.crack_img = self.cracks[0]

            dt_scale = 1
            for freeze in self.freeze_stack[::-1]:
                dt_scale = min(freeze[0], dt_scale)
                freeze[1] = max(0, freeze[1] - self.e['Window'].dt)
                if not freeze[1]:
                    self.freeze_stack.remove(freeze)
            
            if self.e['State'].effect_active('slow_motion'):
                dt_scale *= 0.65

            self.e['Window'].dt = min(self.e['Window'].dt * dt_scale, 0.1)

            if self.controller_mode:
                aim_offset = self.e['Controllers'].read_stick('aim_x', 'aim_y')
                if self.e['Settings'].aim_assist:
                    aim_offset = self.aim_assist.apply(aim_offset)
                if any(aim_offset):
                    aim_offset[0] *= 100
                    aim_offset[1] *= 100
                    self.controller_aim_offset = aim_offset.copy()
                self.mpos = (self.e['Game'].player.center[0] + self.controller_aim_offset[0] - self.camera[0], self.e['Game'].player.center[1] + self.controller_aim_offset[1] - self.camera[1])
            else:
                window_aspect = self.e['Window'].dimensions[0] / self.e['Window'].dimensions[1]
                intended_aspect = 16 / 9
                if window_aspect >= intended_aspect:
                    playable_area = pygame.Rect(0, 0, self.e['Window'].dimensions[1] * intended_aspect, self.e['Window'].dimensions[1])
                else:
                    playable_area = pygame.Rect(0, 0, self.e['Window'].dimensions[0], self.e['Window'].dimensions[0] / intended_aspect)
                playable_area.x = (self.e['Window'].dimensions[0] - playable_area.width) / 2
                playable_area.y = (self.e['Window'].dimensions[1] - playable_area.height) / 2
                relative_mpos = ((self.e['Mouse'].pos[0] - playable_area.x) / playable_area.width, (self.e['Mouse'].pos[1] - playable_area.y) / playable_area.height)
                self.mpos = (relative_mpos[0] * self.e['Game'].display.get_width(), relative_mpos[1] * self.e['Game'].display.get_height())

            # clear aim assist log after handling aim but before other entities would fill it again
            self.machines.machines_in_range = []

            self.handle_controller_switch()

            self.camera.update()

            if not self.e['PauseMenu'].paused:
                self.e['EntityGroups'].update()
            self.e['EntityGroups'].renderz(offset=self.camera)

            if not self.e['PauseMenu'].paused:
                self.machines.update()
            else:
                self.machines.paused_update()
            self.machines.render()

            if not self.e['PauseMenu'].paused:
                self.state.update()
            self.state.render()

            self.menus.update()
            self.menus.render()

            self.music.update()

            if not self.e['PauseMenu'].paused:
                self.tilemap.update()
            self.tilemap.render()
            if not self.machines.high_life:
                if self.e['Settings'].grass_breeze:
                    self.e['Renderer'].renderf(self.gm.update_render, self.e['Window'].dt, offset=self.camera, rot_function=lambda x, y: int((math.sin(x / 100 + time.time() * 1.5) - 0.7) * 30) / 10, z=-5, ignore_tiles=set(self.machines.machine_map))
                elif self.e['Settings'].grass_visible:
                    self.e['Renderer'].renderf(self.gm.update_render, self.e['Window'].dt, offset=self.camera, rot_function=lambda x, y: 0, z=-5, ignore_tiles=set(self.machines.machine_map))
            else:
                self.hlmap.render()

            self.minimap.update()

            self.transition.update()
            self.transition.render()

            self.hud.update()
            self.hud.render()

            self.e['Renderer'].cycle({'default': self.display, 'ui': self.hud_surf})

            self.snow.update()
            self.snow.render()

            self.e['Window'].cycle({
                'surface': self.display,
                'hud_surf': self.hud_surf,
                'noise_tex': self.noise_tex,
                'time': self.e['Window'].runtime,
                'scroll': self.camera.int_pos,
                'border_discard': self.e['Window'].border_discard,
                'saturation': self.e['Settings'].saturation,
                'in_void': int(bool(self.machines.high_life) or (self.e['State'].season == 'void')),
                'static_noise_tex': self.static_noise_tex,
                'crt_filter_tex': self.crt_filter_tex,
                'dimensions': self.e['Window'].dimensions,
                'crt_effect': self.e['Settings'].crt_effect,
                'crack_tex': self.crack_img,
                'power_off': max(0, min(1, (self.e['PauseMenu'].victory - 6) * 2))
            })

            self.presence.update()
            
    Game().run()

except Exception as e:
    CRASH_REPORTER.handle_report()
    raise e