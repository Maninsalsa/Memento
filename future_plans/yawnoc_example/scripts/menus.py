import sys
import math

import pygame

from . import pygpen as pp

from .bezier import generate_line_chain_vfx
from .weapon import Weapon, WEAPON_STATS, WEAPON_NAMES
from .const import SETTINGS, DIFFICULTY_OPTIONS, DIFFICULTY_INFO, DEMO, VERSION, WEAPON_ABILITY_INFO, ENCHANTS, UPGRADE_INFO, UPGRADE_LIST, MACHINE_INFO, AUTOMATA_INFO, raw_enchant_stat, generate_description
from .machines import MACHINE_TYPES, ENEMY_MACHINES
from .util import nice_round

MENU_WEAPONS = ['rifle', 'pistol', 'shotgun']

MAIN_MENU_OPTIONS = ['Play', 'Catalog', 'Options', 'Quit']
if DEMO:
    MAIN_MENU_OPTIONS.insert(3, 'Wishlist')

WEAPON_UNLOCKS = {
    'rifle': 0,
    'pistol': 4,
    'shotgun': 8,
}

SETTING_SUBMENUS = ['Video', 'Graphics', 'Audio', 'Keyboard Input', 'Controller Input', 'Accessibility', 'Reset Save', 'Back']

CATALOG_TABS = ['Weapons', 'Enchants', 'Upgrades', 'Machines', 'Automata']

class Menus(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.weapon_ui_beziers = [generate_line_chain_vfx('weapon_select_description_long', 'slow_in', [0, 0]), generate_line_chain_vfx('weapon_select_description', 'slow_in', [0, 0])]
        self.main_ui_beziers = [generate_line_chain_vfx('menu_item_text_large', 'slow_in', [0, 0]) for i in range(len(MAIN_MENU_OPTIONS))]
        self.last_hover = None
        self.last_hover_2 = None

        # default beziers to hidden
        for bezier in self.weapon_ui_beziers + self.main_ui_beziers:
            bezier.rate = -abs(bezier.rate)

        self.submenu = 'title'

        self.x_offset = 0
        self.next_menu = None

        self.settings_hover_i = 0
        self.pointer_anim = self.e['EntityDB']['misc'].animations['pointer'].copy()
        self.menu_hover_i = 0

        self.settings_submenu = None
        self.updating_binding = None
        self.last_settings_list = None

        self.selected_weapon = 0
        self.selected_difficulty = 1

        self.catalog_selection = [CATALOG_TABS[0], 0, 0]

        self.wishlisted = False

        self.catalog_enchant_mode = False

        self.load_temp_video_settings()

        if self.e['Settings'].steamdeck:
            if 'fullscreen' in SETTINGS:
                del SETTINGS['fullscreen']

    @property
    def cm(self):
        return self.e['Game'].controller_mode
    
    @property
    def interacted(self):
        return self.e['Input'].pressed('shoot') or self.e['Controllers'].pressed('interact')
    
    @property
    def video_settings_changed(self):
        for setting in self.video_settings_temp:
            if setting in self.video_settings_backup:
                if self.video_settings_temp[setting] != self.video_settings_backup[setting]:
                    return True
        return False
    
    def load_temp_video_settings(self):
        self.video_settings_temp = {setting: self.e['Settings'].setting(setting) for setting in self.e['Settings'].settings_save if (setting in SETTINGS) and (SETTINGS[setting]['submenu'] == 'video')}
        self.video_settings_backup = {setting: self.e['Settings'].setting(setting) for setting in self.e['Settings'].settings_save if (setting in SETTINGS) and (SETTINGS[setting]['submenu'] == 'video')}
    
    def apply_temp_video_settings(self):
        for setting in self.video_settings_temp:
            self.e['Settings'].update(setting, self.video_settings_temp[setting], save=False)
    
    def revert_video_settings(self):
        for setting in self.video_settings_backup:
            self.e['Settings'].update(setting, self.video_settings_backup[setting], save=False)
        self.load_temp_video_settings()

    def save_video_settings(self):
        self.e['Settings'].save()
        self.load_temp_video_settings()
    
    def consume_interaction(self):
        self.e['Input'].consume('shoot')
        self.e['Controllers'].consume('interact')

    def update(self):
        for bezier in self.weapon_ui_beziers + self.main_ui_beziers:
            bezier.update(self.e['Window'].dt)
        if self.e['Controllers'].nav_pressed('move_y', 'move_x') or self.e['Controllers'].pressed('menu_down'):
            self.shift_selection(1)
        if self.e['Controllers'].nav_pressed_neg('move_y', 'move_x') or self.e['Controllers'].pressed('menu_up'):
            self.shift_selection(-1)

        if self.e['Input'].pressed('pause') or self.e['Controllers'].pressed('back'):
            if self.submenu == 'weapon_select':
                self.next_menu = 'title'
            if self.submenu == 'catalog':
                self.next_menu = 'title'
            if self.submenu == 'settings':
                if self.settings_submenu:
                    self.settings_submenu = None
                elif self.e['PauseMenu'].temp_main_menu:
                    self.e['PauseMenu'].reset()
                    self.e['PauseMenu'].pause()
                    self.e['State'].title = False
                    self.e['Input'].consume('pause')
                    self.e['Controllers'].consume('back')
                else:
                    self.next_menu = 'title'
            self.e['Sounds'].play('tap')

    def shift_selection(self, offset):
        if self.e['State'].title:
            if self.submenu == 'settings':
                if self.last_settings_list:
                    self.settings_hover_i = (self.settings_hover_i + offset) % len(self.last_settings_list)
                    self.e['Sounds'].play('tap')
            if self.submenu == 'title':
                self.menu_hover_i = (self.menu_hover_i + offset) % len(MAIN_MENU_OPTIONS)
            if self.submenu == 'weapon_select':
                self.menu_hover_i = (self.menu_hover_i + offset) % 3
                if self.menu_hover_i != 2:
                    self.e['Sounds'].play('tap')
            if offset:
                self.pointer_anim.reset()

    def end_title(self):
        self.e['State'].title = False
        self.e['State'].shopping = 1
        self.e['State'].shop_land()
        if self.e['State'].season == 'fall':
            self.e['Music'].play('fall_shop')
        elif self.e['State'].season == 'winter':
            self.e['Music'].play('winter_shop')
        elif self.e['State'].season == 'void':
            self.e['Music'].play('void_shop')
        else:
            self.e['Music'].play('summer_shop')

    def unlocked(self, weapon):
        return WEAPON_UNLOCKS[weapon] <= self.e['State'].record
    
    def get_binding_name(self, binding):
        if binding[0] == 'mouse':
            if 0 < binding[1] < 6:
                return ['mouse left', 'mouse wheel', 'mouse right', 'mouse scroll up', 'mouse scroll down'][binding[1] - 1]
            return '???'
        elif binding[0] == 'button':
            return pygame.key.name(binding[1])
        return '???'
    
    def binding_callback(self, new_binding):
        self.e['Input'].config[self.updating_binding] = new_binding
        self.e['Input'].save_config()
        self.updating_binding = None

    def reset_save_callback(self, result):
        if result:
            self.e['State'].popup = ['Really?', 200, self.reset_save_callback_2, 0]

    def reset_save_callback_2(self, result):
        if result:
            self.e['State'].reset_save()

    def apply_video_settings_callback(self, result):
        # if keeping changes
        if result:
            self.save_video_settings()
        else:
            self.revert_video_settings()

    def exit_callback(self, result):
        if result:
            self.wishlisted = True
            self.e['Steamworks'].open_store_page()
        else:
            pygame.quit()
            sys.exit()

    def demo_win_callback(self, result):
        if result:
            self.e['Steamworks'].open_store_page()
        self.wishlisted = True

    def render(self):
        new_hover = None
        new_hover_2 = None
        if self.e['State'].title:
            if self.next_menu:
                self.x_offset += (200 - self.x_offset) * self.e['Window'].dt * 3
                if self.x_offset > 180:
                    self.submenu = self.next_menu
                    self.next_menu = None
            else:
                self.x_offset += -self.x_offset * self.e['Window'].dt * 7
                if self.x_offset < 0.5:
                    self.x_offset = 0

            self.pointer_anim.update(self.e['Window'].dt)

            if self.submenu == 'catalog':
                tab_x_offset = 0
                for i, tab in enumerate(CATALOG_TABS):
                    alpha = 180
                    if tab == self.catalog_selection[0]:
                        alpha = 255
                    tab_w = self.e['Text']['large_font'].width(tab)
                    tab_r = pygame.Rect(26 + tab_x_offset, 10 - self.x_offset, tab_w, 14)
                    y_offset = 0
                    if tab_r.collidepoint(self.e['Game'].mpos):
                        if alpha < 200:
                            alpha = 200
                            y_offset = math.sin(self.e['Window'].time * 4) * 2
                        if self.last_hover != i:
                            self.e['Sounds'].play('tap')
                        new_hover = i
                        if self.interacted:
                            self.e['Sounds'].play('tap')
                            self.catalog_selection = [tab, 0, 0]
                    self.e['Text']['large_font'].renderzb(tab, (30 + tab_x_offset, 5 - self.x_offset + y_offset), color=(254, 252, 211, alpha), bgcolor=(38, 27, 46, alpha), z=9999, group='ui')
                    tab_x_offset += tab_w + 10

                full_fade = pygame.Surface(self.e['Game'].display.get_size(), pygame.SRCALPHA)
                full_fade.fill((38, 27, 46, max(0, 50 - self.x_offset)))
                top_bar = pygame.Surface((self.e['Game'].display.get_width(), 26), pygame.SRCALPHA)
                top_bar.fill((38, 27, 46, 140))
                side_bar = pygame.Surface((140, self.e['Game'].display.get_height()), pygame.SRCALPHA)
                side_bar.fill((38, 27, 46, 140))
                self.e['Renderer'].blit(top_bar, (0, -self.x_offset), group='ui', z=9990)
                self.e['Renderer'].blit(side_bar, (self.e['Game'].display.get_width() - 140 + self.x_offset, max(0, 27 - self.x_offset)), group='ui', z=9990)
                self.e['Renderer'].renderf(pygame.draw.line, (254, 252, 211), (0, 26 - self.x_offset), (self.e['Game'].display.get_width(), 26 - self.x_offset), group='ui', z=9991)
                self.e['Renderer'].renderf(pygame.draw.line, (254, 252, 211), (self.e['Game'].display.get_width() - 140 + self.x_offset, 27 - self.x_offset), (self.e['Game'].display.get_width() - 140 + self.x_offset, self.e['Game'].display.get_height()), group='ui', z=9991)
                self.e['Renderer'].renderf(pygame.draw.line, (38, 27, 46), (0, 27 - self.x_offset), (self.e['Game'].display.get_width(), 27 - self.x_offset), group='ui', z=9991)
                self.e['Renderer'].renderf(pygame.draw.line, (38, 27, 46), (self.e['Game'].display.get_width() - 141 + self.x_offset, 27 - self.x_offset), (self.e['Game'].display.get_width() - 141 + self.x_offset, self.e['Game'].display.get_height()), group='ui', z=9991)
                self.e['Renderer'].blit(full_fade, (0, 0), group='ui', z=9989)

                item_list = []
                item_size = (16, 16)
                if self.catalog_selection[0] == 'Weapons':
                    item_list = [(item in self.e['State'].catalog['weapons'], item) for item in WEAPON_STATS]
                    item_size = (30, 16)
                if self.catalog_selection[0] == 'Enchants':
                    item_list = [(item in self.e['State'].catalog['enchantments'], item) for item in ENCHANTS]
                    item_size = (68, 10)
                if self.catalog_selection[0] == 'Upgrades':
                    item_list = [(item in self.e['State'].catalog['upgrades'], item) for item in UPGRADE_LIST]
                if self.catalog_selection[0] == 'Machines':
                    item_list = [(item in self.e['State'].catalog['machines'], item) for item in MACHINE_TYPES if item in ENEMY_MACHINES]
                if self.catalog_selection[0] == 'Automata':
                    item_list = [(item in self.e['State'].catalog['automata'], item) for item in AUTOMATA_INFO]
                    item_size = (120, 10)

                gap = 2
                col_count = math.floor(220 / (item_size[0] + gap))

                if self.e['Controllers'].nav_pressed('move_y', 'move_x') or self.e['Controllers'].pressed('menu_down'):
                    self.catalog_selection[2] += 1
                    if self.catalog_selection[2] * col_count + self.catalog_selection[1] >= len(item_list):
                        self.catalog_selection[2] = 0
                    self.e['Sounds'].play('tap')
                if self.e['Controllers'].nav_pressed_neg('move_y', 'move_x') or self.e['Controllers'].pressed('menu_up'):
                    self.catalog_selection[2] -= 1
                    if self.catalog_selection[2] < 0:
                        if (len(item_list) - 1) % col_count >= self.catalog_selection[1]:
                            self.catalog_selection[2] = math.floor((len(item_list) - 1) / col_count)
                        else:
                            self.catalog_selection[2] = math.floor((len(item_list) - 1) / col_count) - 1
                    self.e['Sounds'].play('tap')
                if self.e['Controllers'].nav_pressed('move_x', 'move_y') or self.e['Controllers'].pressed('menu_right'):
                    self.catalog_selection[1] += 1
                    if (self.catalog_selection[1] >= col_count) or (self.catalog_selection[1] + self.catalog_selection[2] * col_count >= len(item_list)):
                        self.catalog_selection[1] = 0
                    self.e['Sounds'].play('tap')
                if self.e['Controllers'].nav_pressed_neg('move_x', 'move_y') or self.e['Controllers'].pressed('menu_left'):
                    self.catalog_selection[1] -= 1
                    if self.catalog_selection[1] < 0:
                        remainder = len(item_list) % col_count
                        if self.catalog_selection[1] + self.catalog_selection[2] * col_count + 1 >= len(item_list) - remainder:
                            self.catalog_selection[1] = max(remainder - 1, 0)
                        else:
                            self.catalog_selection[1] = col_count - 1
                    self.e['Sounds'].play('tap')

                category = self.catalog_selection[0]
                for i, item in enumerate(item_list):
                    x = i % col_count
                    y = i // col_count
                    img = None
                    selected = tuple(self.catalog_selection[1:]) == (x, y)
                    alpha = 255 if selected else 180
                    if category == 'Weapons':
                        suffix = '_icon' if item[0] else '_flat'
                        img = self.e['Assets'].images['weapons'][f'{item[1]}{suffix}']
                    if category == 'Upgrades':
                        if item[0]:
                            img = self.e['Assets'].images['upgrades'][f'{item[1]}_b']
                        else:
                            img = self.e['Assets'].images['upgrades']['unknown_b']
                    if category == 'Machines':
                        suffix = '' if item[0] else '_white'
                        img = self.e['Assets'].images['machines'][f'{item[1]}{suffix}']
                    
                    topleft = (8 - self.x_offset * 2, 45)
                    center = (topleft[0] + item_size[0] / 2 + x * (item_size[0] + gap), topleft[1] + item_size[1] / 2 + y * (item_size[1] + gap))
                    rect = pygame.Rect(center[0] - item_size[0] / 2, center[1] - item_size[1] / 2, item_size[0], item_size[1])
                    if rect.collidepoint(self.e['Game'].mpos):
                        center = (center[0], center[1] - 2)
                        if self.last_hover_2 != i:
                            self.e['Sounds'].play('tap')
                        new_hover_2 = i
                        if self.interacted:
                            self.catalog_selection[1] = x
                            self.catalog_selection[2] = y
                            self.e['Sounds'].play('tap')
                    if img:
                        img = img.copy()
                        img.set_alpha(alpha)
                        self.e['Renderer'].blit(img, (center[0] - img.get_width() / 2, center[1] - img.get_height() / 2), group='ui', z=9999)
                        if category == 'Weapons':
                            weapon = Weapon(item[1], self.e['Game'].player)
                            weapon.render_stars((center[0] - img.get_width() / 2, center[1] + img.get_height() / 2 - 3), group='ui', z=9999)
                        if category == 'Machines':
                            self.e['Renderer'].renderf(pp.gfx_util.outline, img, (center[0] - img.get_width() / 2, center[1] - img.get_height() / 2), (38, 27, 46, 255 if (alpha == 255) else 80), group='ui', z=9998)
                    else:
                        item_name = 'unknown'
                        if category == 'Enchants':
                            item_name = ENCHANTS[item[1]]['name']
                        if category == 'Automata':
                            item_name = AUTOMATA_INFO[item[1]]['name']
                        if category == 'Automata':
                            pass
                        item_text = item_name if item[0] else '???'
                        self.e['Text']['small_font'].renderzb(item_text, (center[0] - self.e['Text']['small_font'].width(item_text) / 2, center[1] - item_size[1] / 2), color=(254, 252, 211, alpha if (alpha == 255) else 120), bgcolor=(38, 27, 46), z=9999, group='ui')

                try:
                    selection = item_list[self.catalog_selection[1] + self.catalog_selection[2] * col_count]
                except IndexError:
                    selection = [None, None]
                if category != 'Weapons':
                    name = 'Undiscovered'
                    description = '???'
                    if selection[0]:
                        if category == 'Enchants':
                            name = ENCHANTS[selection[1]]['name']
                            description = ENCHANTS[selection[1]]['text'].replace('<stat>', str(nice_round(raw_enchant_stat(selection[1], 1) * 100, 1)))
                        if category == 'Upgrades':
                            name = UPGRADE_INFO[selection[1]]['name']
                            description = generate_description(selection[1], 1)
                        if category == 'Machines':
                            name = MACHINE_INFO[selection[1]]['name']
                            description = MACHINE_INFO[selection[1]]['description']
                        if category == 'Automata':
                            name = AUTOMATA_INFO[selection[1]]['name']
                            description = AUTOMATA_INFO[selection[1]]['description']
                    description = self.e['Text']['small_font'].prep_text(description, line_width=132).text
                    self.e['Text']['small_font'].renderzb(name, (self.e['Game'].display.get_width() - 134 + self.x_offset, 33), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                    self.e['Text']['small_font'].renderzb(description, (self.e['Game'].display.get_width() - 134 + self.x_offset, 45), color=(205, 209, 201), bgcolor=(38, 27, 46), z=9999, group='ui')
                else:
                    name = 'Undiscovered'
                    description = '???'
                    weapon = Weapon(selection[1], self.e['Game'].player)
                    if selection[0]:
                        name = WEAPON_STATS[selection[1]]['name']
                        description = WEAPON_STATS[selection[1]]['desc']
                        desc_prepped = self.e['Text']['small_font'].prep_text(description, line_width=132)
                        desc_h = desc_prepped.height
                        description = desc_prepped.text
                        if self.catalog_enchant_mode:
                            self.e['State'].render_weapon_enchants_compressed(weapon, (self.e['Game'].display.get_width() - 134 + self.x_offset, 52 + desc_h))
                        else:
                            primary_id = WEAPON_STATS[selection[1]]['primary']
                            secondary_id = WEAPON_STATS[selection[1]]['secondary']
                            self.e['Renderer'].blit(self.e['Assets'].images['upgrades'][f'{primary_id}_b'], (self.e['Game'].display.get_width() - 134 + self.x_offset, 48 + desc_h), group='ui', z=9999)
                            primary_name = WEAPON_ABILITY_INFO[primary_id]['name']
                            self.e['Text']['small_font'].renderzb(primary_name, (self.e['Game'].display.get_width() - 115 + self.x_offset, 52 + desc_h), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                            primary_desc = WEAPON_ABILITY_INFO[primary_id]['description']
                            primary_desc_prepped = self.e['Text']['small_font'].prep_text(primary_desc, line_width=132)
                            primary_desc_h = primary_desc_prepped.height
                            primary_desc = primary_desc_prepped.text
                            self.e['Text']['small_font'].renderzb(primary_desc, (self.e['Game'].display.get_width() - 134 + self.x_offset, 65 + desc_h), color=(205, 209, 201), bgcolor=(38, 27, 46), z=9999, group='ui')
                            self.e['Renderer'].blit(self.e['Assets'].images['upgrades'][f'{secondary_id}_b'], (self.e['Game'].display.get_width() - 134 + self.x_offset, 69 + desc_h + primary_desc_h), group='ui', z=9999)
                            secondary_name = WEAPON_ABILITY_INFO[secondary_id]['name']
                            self.e['Text']['small_font'].renderzb(secondary_name, (self.e['Game'].display.get_width() - 115 + self.x_offset, 73 + desc_h + primary_desc_h), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                            secondary_desc = WEAPON_ABILITY_INFO[secondary_id]['description']
                            secondary_desc_prepped = self.e['Text']['small_font'].prep_text(secondary_desc, line_width=132)
                            secondary_desc_h = secondary_desc_prepped.height
                            secondary_desc = secondary_desc_prepped.text
                            secondary_desc = self.e['Text']['small_font'].prep_text(secondary_desc, line_width=132).text
                            self.e['Text']['small_font'].renderzb(secondary_desc, (self.e['Game'].display.get_width() - 134 + self.x_offset, 86 + desc_h + primary_desc_h), color=(205, 209, 201), bgcolor=(38, 27, 46), z=9999, group='ui')
                    self.e['Text']['small_font'].renderzb(name, (self.e['Game'].display.get_width() - 134 + self.x_offset, 33), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                    self.e['Text']['small_font'].renderzb(description, (self.e['Game'].display.get_width() - 134 + self.x_offset, 45), color=(205, 209, 201), bgcolor=(38, 27, 46), z=9999, group='ui')

                self.e['Text']['small_font'].renderzb('Back', (19 - self.x_offset, self.e['Game'].display.get_height() - 20), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                if self.cm:
                    back_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping['back'])
                    self.e['InputTips'].render_icon(back_img, (-self.x_offset + 8, self.e['Game'].display.get_height() - 21), z=9999)
                back_r = pygame.Rect(0, self.e['Game'].display.get_height() - 22, 36, 10)
                if back_r.collidepoint(self.e['Game'].mpos) and (not self.cm):
                    if self.last_hover != -1:
                        self.e['Sounds'].play('tap')
                        self.pointer_anim.reset()
                    new_hover = -1
                    self.e['Renderer'].blit(self.pointer_anim.img, (-self.x_offset + 8, self.e['Game'].display.get_height() - 20), z=9999, group='ui')
                    if self.interacted:
                        self.next_menu = 'title'
                        self.e['Sounds'].play('tap')

                if category == 'Weapons':
                    mode_switch_text = 'View Enchants'
                    if self.catalog_enchant_mode:
                        mode_switch_text = 'View Abilities'
                    self.e['Text']['small_font'].renderzb(mode_switch_text, (self.e['Game'].display.get_width() - 123 + self.x_offset, self.e['Game'].display.get_height() - 20), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                    if self.cm:
                        switch_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping['interact'])
                        self.e['InputTips'].render_icon(switch_img, (self.e['Game'].display.get_width() - 134 + self.x_offset, self.e['Game'].display.get_height() - 21), z=9999)
                        if self.e['Controllers'].pressed('interact'):
                            self.catalog_enchant_mode = not self.catalog_enchant_mode
                            self.e['Sounds'].play('tap')
                    mode_switch_r = pygame.Rect(self.e['Game'].display.get_width() - 134 + self.x_offset, self.e['Game'].display.get_height() - 21, 76, 10)
                    if mode_switch_r.collidepoint(self.e['Game'].mpos) and (not self.cm):
                        if self.last_hover != -2:
                            self.e['Sounds'].play('tap')
                            self.pointer_anim.reset()
                        new_hover = -2
                        self.e['Renderer'].blit(self.pointer_anim.img, (self.e['Game'].display.get_width() - 134 + self.x_offset, self.e['Game'].display.get_height() - 20), z=9999, group='ui')
                        if self.interacted:
                            self.catalog_enchant_mode = not self.catalog_enchant_mode
                            self.e['Sounds'].play('tap')
                
                if self.cm:
                    tab_left_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping['dodge'])
                    tab_right_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping['swap'])
                    self.e['InputTips'].render_icon(tab_left_img, (10, 8 - self.x_offset), z=9999)
                    self.e['InputTips'].render_icon(tab_right_img, (self.e['Game'].display.get_width() - tab_right_img.get_width() - 10, 8 - self.x_offset), z=9999)
                
                if self.e['Controllers'].pressed('swap'):
                    self.catalog_selection = [CATALOG_TABS[(CATALOG_TABS.index(self.catalog_selection[0]) + 1) % len(CATALOG_TABS)], 0, 0]
                    self.e['Sounds'].play('tap')
                if self.e['Controllers'].pressed('dodge'):
                    self.catalog_selection = [CATALOG_TABS[(CATALOG_TABS.index(self.catalog_selection[0]) - 1) % len(CATALOG_TABS)], 0, 0]
                    self.e['Sounds'].play('tap')

            if self.submenu == 'settings':
                self.e['Renderer'].blit(self.e['Assets'].images['misc']['full_fade'], (-self.x_offset, 0), z=9000, group='ui')

                setting_gap = 140
                setting_y_gap = 13
                if not self.settings_submenu:
                    setting_list = {setting.lower(): {'name': setting, 'options': []} for setting in SETTING_SUBMENUS}
                    if self.e['PauseMenu'].temp_main_menu:
                        if 'reset save' in setting_list:
                            del setting_list['reset save']
                elif self.settings_submenu.lower() == 'keyboard input':
                    setting_list = {binding: {'name': binding.replace('_', ' '), 'options': [], 'value': self.get_binding_name(self.e['Input'].config[binding])} for binding in self.e['Input'].config if binding != '__backspace'}
                    setting_list['reset'] = {'name': 'Reset Bindings', 'options': []}
                    setting_list['back'] = {'name': 'Back', 'options': []}
                elif self.settings_submenu.lower() == 'controller input':
                    if self.e['Controllers'].last:
                        setting_list = {
                            'modify_info': {'name': 'Modify mapping in settings/controller_<guid>.json', 'options': []},
                            'device_id': {'name': f'Controller GUID: {self.e["Controllers"].last.guid}', 'options': []},
                            'device_name': {'name': f'Controller Name: {self.e["Controllers"].last.name}', 'options': []},
                            'swap_trigger_bumper': SETTINGS['swap_trigger_bumper'],
                            'back': {'name': 'Back', 'options': []},
                        }
                    else:
                        setting_list = {
                            'warning': {'name': 'No controller detected!', 'options': []},
                            'back': {'name': 'Back', 'options': []},
                        }
                elif self.settings_submenu:
                    setting_list = {setting: SETTINGS[setting] for setting in SETTINGS if (SETTINGS[setting]['submenu'] == self.settings_submenu.lower()) or (setting == 'back')}
                    if self.settings_submenu == 'video':
                        setting_list['apply'] = {'name': 'Apply', 'options': []}
                        if self.video_settings_changed:
                            setting_list['back']['name'] = 'Cancel'
                        else:
                            setting_list['back']['name'] = 'Back'

                self.last_settings_list = setting_list

                for i, setting in enumerate(setting_list):
                    current_selection = self.video_settings_temp[setting] if (self.settings_submenu == 'video') and (setting in self.video_settings_temp) else self.e['Settings'].setting(setting)
                    setting_r = pygame.Rect(0, 13 + i * setting_y_gap, setting_gap + 30, 12)
                    hovering = setting_r.collidepoint(self.e['Game'].mpos)
                    if hovering or (self.cm and (self.settings_hover_i == i)):
                        if not self.cm:
                            if i != self.settings_hover_i:
                                self.pointer_anim.reset()
                                self.e['Sounds'].play('tap')
                            self.settings_hover_i = i
                        if self.interacted:
                            if setting == 'back':
                                if self.settings_submenu:
                                    if self.settings_submenu == 'video':
                                        self.load_temp_video_settings()
                                    self.settings_submenu = None
                                    self.e['Sounds'].play('tap')
                                    self.settings_hover_i = 0
                                elif self.e['PauseMenu'].temp_main_menu:
                                    self.e['PauseMenu'].reset()
                                    self.e['PauseMenu'].pause()
                                    self.e['State'].title = False
                                else:
                                    self.next_menu = 'title'
                                    self.e['Sounds'].play('tap')
                                self.consume_interaction()
                            elif setting == 'apply':
                                self.apply_temp_video_settings()
                                self.e['State'].popup = ['Keep changes? Reverting in\n[TIMER]s.', 200, self.apply_video_settings_callback, 0, ['Revert', 'Keep'], 10]
                            elif setting == 'reset save':
                                self.e['State'].popup = ['Are you sure you want to delete your save data?', 200, self.reset_save_callback, 0]
                                self.e['Sounds'].play('tap')
                                self.consume_interaction()
                            elif setting_list[setting]['name'] in SETTING_SUBMENUS:
                                self.settings_hover_i = 0
                                self.settings_submenu = setting
                                self.e['Sounds'].play('tap')
                                self.consume_interaction()
                            elif setting in self.e['Input'].config:
                                self.e['Input'].binding_listen_callback(self.binding_callback)
                                self.updating_binding = setting
                                self.e['Sounds'].play('tap')
                                self.consume_interaction()
                            elif setting == 'reset':
                                self.e['Input'].load_config('data/config/key_mappings_default.json')
                                self.e['Input'].save_config()
                    self.e['Text']['small_font'].renderzb(setting_list[setting]['name'], (-self.x_offset + 19, 16 + i * setting_y_gap), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                    if 'value' in setting_list[setting]:
                        if setting == self.updating_binding:
                            setting_list[setting]['value'] = '<press>'
                        self.e['Text']['small_font'].renderzb(setting_list[setting]['value'], (-self.x_offset + 6 + setting_gap - self.e['Text']['small_font'].width(setting_list[setting]['value']) / 2, 16 + i * setting_y_gap), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                    if self.settings_hover_i == i:
                        self.e['Renderer'].blit(self.pointer_anim.img, (-self.x_offset + 8, 15 + i * setting_y_gap), z=9999, group='ui')
                    if current_selection:
                        self.e['Text']['small_font'].renderzb(current_selection, (-self.x_offset + 6 + setting_gap - self.e['Text']['small_font'].width(current_selection) / 2, 16 + i * setting_y_gap), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9999, group='ui')
                        if self.settings_hover_i == i:
                            left_r = pygame.Rect(-self.x_offset - 6 + setting_gap - self.e['Text']['small_font'].width(current_selection) / 2 - 2, 14 + i * setting_y_gap, 10, 10)
                            right_r = pygame.Rect(-self.x_offset + 12 + setting_gap + self.e['Text']['small_font'].width(current_selection) / 2 - 2, 14 + i * setting_y_gap, 10, 10)
                            left_img = self.e['Assets'].images['misc']['arrow_l'].copy()
                            right_img = self.e['Assets'].images['misc']['arrow_r'].copy()
                            if left_r.collidepoint(self.e['Game'].mpos) or self.cm:
                                left_img.set_alpha(255)
                                if (self.e['Input'].pressed('shoot') and not self.cm) or (self.cm and self.e['Controllers'].nav_pressed_neg('move_x', 'move_y')) or self.e['Controllers'].pressed('menu_left'):
                                    if self.settings_submenu == 'video':
                                        self.video_settings_temp[setting] = setting_list[setting]['options'][(setting_list[setting]['options'].index(current_selection) - 1) % len(setting_list[setting]['options'])]
                                    else:
                                        self.e['Settings'].update(setting, setting_list[setting]['options'][(setting_list[setting]['options'].index(current_selection) - 1) % len(setting_list[setting]['options'])])
                                    self.e['Sounds'].play('tap')
                            else:
                                left_img.set_alpha(100)
                            if right_r.collidepoint(self.e['Game'].mpos) or self.cm:
                                right_img.set_alpha(255)
                                if (self.e['Input'].pressed('shoot') and not self.cm) or (self.cm and self.e['Controllers'].nav_pressed('move_x', 'move_y')) or self.e['Controllers'].pressed('menu_right'):
                                    if self.settings_submenu == 'video':
                                        self.video_settings_temp[setting] = setting_list[setting]['options'][(setting_list[setting]['options'].index(current_selection) + 1) % len(setting_list[setting]['options'])]
                                    else:
                                        self.e['Settings'].update(setting, setting_list[setting]['options'][(setting_list[setting]['options'].index(current_selection) + 1) % len(setting_list[setting]['options'])])
                                    self.e['Sounds'].play('tap')
                            else:
                                right_img.set_alpha(100)
                            self.e['Renderer'].blit(left_img, (-self.x_offset - 6 + setting_gap - self.e['Text']['small_font'].width(current_selection) / 2 + math.cos(self.e['Window'].time * 3) * 0.7, 14 + i * setting_y_gap), group='ui', z=9999)
                            self.e['Renderer'].blit(right_img, (-self.x_offset + 12 + setting_gap + self.e['Text']['small_font'].width(current_selection) / 2 - math.cos(self.e['Window'].time * 3) * 0.7, 14 + i * setting_y_gap), group='ui', z=9999)

            elif self.submenu == 'title':
                title_img = self.e['Assets'].images['misc']['title']
                self.e['Renderer'].blit(title_img, (self.e['Game'].display.get_width() / 2 - title_img.get_width() / 2, 26 + (1 if self.e['Window'].time % 1 < 0.25 else 0) - self.x_offset), z=9999, group='ui')
                if DEMO:
                    demo_img = self.e['Assets'].images['misc']['demo']
                    demo_img.set_alpha(200)
                    self.e['Renderer'].blit(demo_img, (self.e['Game'].display.get_width() / 2 + 28, 48 + (1 if (self.e['Window'].time - 0.1) % 1 < 0.25 else 0) - self.x_offset), z=9998, group='ui')

                version_string = f'v{VERSION}'
                self.e['Text']['small_font'].renderzb(version_string, (self.e['Game'].display.get_width() - 4 - self.e['Text']['small_font'].width(version_string), self.e['Game'].display.get_height() - 10 + self.x_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')

                for i, option in enumerate(MAIN_MENU_OPTIONS):
                    bezier = self.main_ui_beziers[i]
                    y_offset = min(bezier.time * 10, 4)
                    pos = (-self.x_offset, self.e['Game'].display.get_height() - (len(MAIN_MENU_OPTIONS) - i) * 24 - y_offset)
                    option_r = pygame.Rect(pos[0] - 1, pos[1] - 5 + y_offset, 104, 16)
                    hovering = option_r.collidepoint(self.e['Game'].mpos)
                    if hovering:
                        self.menu_hover_i = i
                    alpha = 140 + min(bezier.time * 400, 65)
                    self.e['Text']['large_font'].renderzb(option, (pos[0] + 6, pos[1]), color=(254, 252, 211, alpha + 50), bgcolor=(38, 27, 46, alpha + 50), z=9999, group='ui')
                    self.e['Renderer'].renderf(bezier.draw, offset=(pos[0], pos[1] + 18), z=9999, group='ui')
                    for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        self.e['Renderer'].renderf(bezier.draw, offset=(pos[0] + offset[0], pos[1] + offset[1] + 18), color=(38, 27, 46), z=9998, group='ui')
                    if hovering or (self.cm and (self.menu_hover_i == i)):
                        if self.last_hover != option:
                            self.e['Sounds'].play('tap')
                        new_hover = option
                        bezier.rate = abs(bezier.rate)
                        if self.interacted:
                            if option == 'Quit':
                                if DEMO and (not self.wishlisted):
                                    self.e['State'].popup = ['Thanks for playing the Yawnoc demo!', 200, self.exit_callback, 0, ['Exit', 'Wishlist']]
                                else:
                                    pygame.quit()
                                    sys.exit()
                            if option == 'Play':
                                self.next_menu = 'weapon_select'
                                self.e['Sounds'].play('tap')
                            if option == 'Options':
                                self.next_menu = 'settings'
                                self.e['Sounds'].play('tap')
                            if option == 'Wishlist':
                                self.e['Steamworks'].open_store_page()
                                self.wishlisted = True
                            if option == 'Catalog':
                                self.next_menu = 'catalog'
                                self.e['Sounds'].play('tap')
                                self.last_hover = 0
                    else:
                        bezier.rate = -abs(bezier.rate)

            elif self.submenu == 'weapon_select':
                self.e['Renderer'].blit(self.e['Assets'].images['misc']['full_fade'], (-self.x_offset, 0), z=9000, group='ui')
                
                if WEAPON_UNLOCKS[list(WEAPON_UNLOCKS)[self.selected_weapon]] <= self.e['State'].record:
                    self.e['Game'].player.weapon = Weapon(list(WEAPON_UNLOCKS)[self.selected_weapon], self.e['Game'].player)
                self.e['State'].difficulty_set = self.selected_difficulty

                for i in range(3):
                    if i < 2:
                        bezier = self.weapon_ui_beziers[i]
                        y_offset = 40 * i
                        self.e['Text']['large_font'].renderzb(['Difficulty', 'Weapon'][i], (6 - self.x_offset, 6 + y_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')

                        for j in range(3):
                            # difficulties
                            if i == 0:
                                loop_j = (j + self.selected_difficulty - 1) % len(DIFFICULTY_OPTIONS)
                                img = self.e['Assets'].images['difficulties'][str(loop_j)].copy()
                            
                            # weapons
                            if i == 1:
                                loop_j = (j + self.selected_weapon - 1) % len(WEAPON_UNLOCKS)
                                weapon = list(WEAPON_UNLOCKS)[loop_j]
                                img = self.e['Assets'].images['weapons'][f'{weapon}_icon'].copy()
                                if WEAPON_UNLOCKS[weapon] > self.e['State'].record:
                                    img = self.e['Assets'].images['misc']['lock'].copy()

                            if j != 1:
                                img.set_alpha(165)
                            
                            self.e['Renderer'].blit(img, (30 - self.x_offset + j * 14 - img.get_width() / 2, 32 + y_offset - img.get_height() / 2), z=9999 if j == 1 else 9998, group='ui')
                        
                        left_r = pygame.Rect(4 - self.x_offset, 24 + y_offset, 10, 16)
                        right_r = pygame.Rect(73 - self.x_offset, 24 + y_offset, 10, 16)

                        full_r = pygame.Rect(0, left_r.y, right_r.right, 16)
                        if full_r.collidepoint(self.e['Game'].mpos):
                            self.menu_hover_i = i

                        left_img = self.e['Assets'].images['misc']['arrow_l'].copy()
                        right_img = self.e['Assets'].images['misc']['arrow_r'].copy()
                        left_img.set_alpha(100)
                        if left_r.collidepoint(self.e['Game'].mpos) or (self.cm and (i == self.menu_hover_i)):
                            left_img.set_alpha(255)
                            if (self.e['Input'].pressed('shoot') and not self.cm) or (self.cm and self.e['Controllers'].nav_pressed_neg('move_x', 'move_y')) or self.e['Controllers'].pressed('menu_left'):
                                if i == 0:
                                    self.selected_difficulty = (self.selected_difficulty - 1) % len(DIFFICULTY_OPTIONS)
                                if i == 1:
                                    self.selected_weapon = (self.selected_weapon - 1) % len(WEAPON_UNLOCKS)
                                self.e['Sounds'].play('tap')
                        right_img.set_alpha(100)
                        if right_r.collidepoint(self.e['Game'].mpos) or (self.cm and (i == self.menu_hover_i)):
                            right_img.set_alpha(255)
                            if (self.e['Input'].pressed('shoot') and not self.cm) or (self.cm and self.e['Controllers'].nav_pressed('move_x', 'move_y')) or self.e['Controllers'].pressed('menu_right'):
                                if i == 0:
                                    self.selected_difficulty = (self.selected_difficulty + 1) % len(DIFFICULTY_OPTIONS)
                                if i == 1:
                                    self.selected_weapon = (self.selected_weapon + 1) % len(WEAPON_UNLOCKS)
                                self.e['Sounds'].play('tap')
                        self.e['Renderer'].blit(left_img, (left_r.x + 2 + (math.cos(self.e['Window'].time * 3) * 0.7 if left_img.get_alpha() == 255 else 0), left_r.y + 3), group='ui', z=9999)
                        self.e['Renderer'].blit(right_img, (right_r.x + 2 - (math.cos(self.e['Window'].time * 3) * 0.7 if right_img.get_alpha() == 255 else 0), right_r.y + 3), group='ui', z=9999)

                        self.e['Renderer'].renderf(bezier.draw, offset=(right_r.right + 5, 32 + y_offset), z=9999, group='ui')
                        for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            self.e['Renderer'].renderf(bezier.draw, offset=(right_r.right + 5 + offset[0], 32 + y_offset + offset[1]), color=(38, 27, 46), z=9998, group='ui')

                        bezier.rate = -abs(bezier.rate)
                        if self.menu_hover_i == i:
                            if self.weapon_ui_beziers[int(not i)].time <= 0:
                                bezier.rate = abs(bezier.rate)

                        if bezier.time:
                            if i == 0:
                                description = f'{DIFFICULTY_INFO[self.selected_difficulty]["name"]}\n{DIFFICULTY_INFO[self.selected_difficulty]["description"]}'
                                self.e['Text']['small_font'].renderzb(description[:int(bezier.time * len(description))], (right_r.right + 16, 31 + y_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')
                            if i == 1:
                                weapon = list(WEAPON_UNLOCKS)[self.selected_weapon]
                                secondary = WEAPON_STATS[weapon]['secondary']
                                secondary_img = self.e['Assets'].images['upgrades'][f'{secondary}_b'].copy()
                                secondary_img.set_alpha(bezier.time * 255)
                                if WEAPON_UNLOCKS[weapon] > self.e['State'].record:
                                    unlock_text = ('Unlocks after', f'wave {WEAPON_UNLOCKS[weapon]}')
                                    self.e['Text']['small_font'].renderzb(unlock_text[0][:int(bezier.time * len(unlock_text[0]))], (right_r.right + 25, 31 + y_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')
                                    self.e['Text']['small_font'].renderzb(unlock_text[1][:int(bezier.time * len(unlock_text[1]))], (right_r.right + 34, 44 + y_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')
                                else:
                                    self.e['Renderer'].blit(secondary_img, (right_r.right + 16, 39 + y_offset), z=9999, group='ui')
                                    self.e['Text']['small_font'].renderzb(WEAPON_NAMES[weapon][:int(bezier.time * len(WEAPON_NAMES[weapon]))], (right_r.right + 25, 31 + y_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')
                                    self.e['Text']['small_font'].renderzb(WEAPON_ABILITY_INFO[secondary]['name'][:int(bezier.time * len(WEAPON_ABILITY_INFO[secondary]['name']))], (right_r.right + 34, 44 + y_offset), color=(254, 252, 211, 255), bgcolor=(38, 27, 46, 255), z=9999, group='ui')
                                
                    else:
                        pos = (-self.x_offset, self.e['Game'].display.get_height() - 24)
                        bezier = self.main_ui_beziers[0]
                        alpha = 140 + min(bezier.time * 400, 65)
                        color = (254, 252, 211, alpha + 50)
                        if WEAPON_UNLOCKS[list(WEAPON_UNLOCKS)[self.selected_weapon]] > self.e['State'].record:
                            color = (191, 60, 96, alpha + 50)
                        self.e['Text']['large_font'].renderzb('Fight', (pos[0] + 6, pos[1]), color=color, bgcolor=(38, 27, 46, 255), z=9999, group='ui')
                        option_r = pygame.Rect(0, pos[1] - 5, 104, 16)
                        hovering = option_r.collidepoint(self.e['Game'].mpos)
                        if hovering:
                            self.menu_hover_i = i

                        if (hovering or (self.cm and (self.menu_hover_i == i))) and (not self.e['Transition'].progress):
                            bezier.rate = abs(bezier.rate)
                            if self.last_hover != i:
                                self.e['Sounds'].play('tap')
                            new_hover = i
                            if self.interacted:
                                if WEAPON_UNLOCKS[list(WEAPON_UNLOCKS)[self.selected_weapon]] <= self.e['State'].record:
                                    self.e['Transition'].transition(self.end_title)
                                    self.e['Sounds'].play('prepare', volume=0.45)
                                else:
                                    self.e['Sounds'].play('denied', volume=0.45)
                        else:
                            bezier.rate = -abs(bezier.rate)

                        self.e['Renderer'].renderf(bezier.draw, offset=(pos[0], pos[1] + 18), z=9999, group='ui')
                        for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            self.e['Renderer'].renderf(bezier.draw, offset=(pos[0] + offset[0], pos[1] + offset[1] + 18), color=(38, 27, 46), z=9998, group='ui')

        self.last_hover = new_hover
        self.last_hover_2 = new_hover_2

    
        