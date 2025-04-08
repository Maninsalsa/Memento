import math
import random

import pygame

from . import pygpen as pp

from .debris import Debris, AbilityDrop
from .drops import Drop
from .bullet import Bullet
from .weapon import Weapon, WEAPON_STATS, ENCHANTS
from .rig import CentipedeRig
from .slash import Slash
from .eye import Eye
from .util import nice_round, roman_numeral
from .machines import ENEMY_MACHINES
from .const import FRENEMY_LEVELS, Difficulties, DEFAULT_SAVE, DEMO, SHOP_UPGRADES, ALL_SHOP_UPGRADES, UPGRADE_INFO, UPGRADE_LIST, AUTOMATA_INFO, OBTAINABLE_POWERUPS, ABILITY_DURATIONS, PRICE_SCALE, ALT_SHOP_PREMIUM, generate_description

SEASON_STATS = {
    'summer': {
        'pause': 1.0,
        'count': 1.0,
        'step': 1.0,
    },
    'fall': {
        'pause': 2.0,
        'count': 0.5,
        'step': 1.0,
    },
    'winter': {
        'pause': 1.0,
        'count': 0.68,
        'step': 1.3,
    },
    'void': {
        'pause': 0.6,
        'count': 1.0,
        'step': 1.0,
    }
}

UPGRADE_INFO.update(WEAPON_STATS)

EFFECTS = {
    'invincibility': 'Invincibility',
    'collateral': 'Collateral Damage',
    'double_barrel': 'Double Barrel',
    'lifesteal': 'Lifesteal',
    'freeze': 'Freeze',
    'extra_rounds': 'Extra Rounds',
    'potion': 'Potion',
    'swiftness': 'Swiftness',
    'deathspiral': 'Death Spiral',
    'storage': 'Storage',
    'miasma': 'Miasma',
    'cleanse': 'Cleanse',
    'rampage': 'Rampage',
    'shield': 'Shield',
    'dash_slash': 'Dash Slash',
    'guard': 'Guard',
    'garys_charm': 'Gary\'s Charm',
    'slow_motion': 'Slow Motion',
    'flame': 'Flame',
    'collector': 'Collector',
    'thunderclap': 'Thunderclap',
}

COOLDOWN_EFFECTS = ['garys_charm', 'cleanse', 'rampage']

def calc_price(base, stacks):
    return int(base * (1.22 ** stacks))

class UpgradeDB(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.options = list(SHOP_UPGRADES)

        self.compute_weights()

    def compute_weights(self):
        self.weights = []
        total = 0
        for upgrade in self.options:
            freq = UPGRADE_INFO[upgrade]['frequency']
            if self.e['State'].owned_upgrades[upgrade]:
                freq *= (1 + self.e['State'].upgrade_stat('frequent_customer'))
            restrictions = UPGRADE_INFO[upgrade]['restrictions'] if 'restrictions' in UPGRADE_INFO[upgrade] else {}
            if ('partner' in restrictions) and (restrictions['partner']):
                if (not self.e['Game'].player) or (not self.e['Game'].player.partner[0]):
                    freq = 0
            if ('owned' in restrictions) and (not restrictions['owned']):
                if self.e['State'].upgrade_stat(upgrade):
                    freq = 0
            if ('minimum_wave' in restrictions) and (restrictions['minimum_wave'] > self.e['State'].wave):
                freq = 0
            if (upgrade == 'potion') and (self.e['State'].difficulty_set == Difficulties.EASY):
                freq = 18
            if (upgrade == 'potion') and (self.e['State'].upgrade_stat('all_natural')):
                freq = 0
            self.weights.append(freq)
            total += freq

        self.weights = [w / total for w in self.weights]

    def shop_select(self):
        return random.choices(population=self.options, weights=self.weights, k=1)[0]
    
    def true_random_select(self, exclude=[]):
        while True:
            upgrade = random.choice(self.options)
            if upgrade not in exclude:
                return upgrade
            

class Interactable(pp.Element):
    def __init__(self, category, subtype, pos, price=0, guide=False):
        super().__init__()

        self.pos = tuple(pos)
        self.category = category
        self.type = subtype
        self.price = price
        self.guide = guide
        
        self.dis = 99999
    
    def render(self):
        guide_range = 300
        if self.e['Tutorial'].state == 4:
            guide_range = 999999
        if (pp.game_math.distance(self.pos, self.e['Game'].player.center) < guide_range) and (self.category == 'next'):
            if not self.e['HUD'].guide_target:
                self.e['HUD'].guide_target = tuple(self.pos)
        
        if self.guide and (self.e['State'].scrap >= self.price):
            self.e['HUD'].guide_target = tuple(self.pos)

        shadow_img = self.e['Assets'].images['misc']['shadow_medium']
        self.dis = pp.utils.game_math.distance(self.pos, self.e['Game'].player.center)
        if self.category == 'next':
            img = self.e['Assets'].images['upgrades']['next']
        elif self.category == 'shop':
            img = self.e['Assets'].images['upgrades'][self.type]
        elif self.category == 'weapon':
            img = self.e['Assets'].images['weapons'][f'{self.type}_icon']
        if self.price:
            price_text = f'{self.price:,}'
            text_width = self.e['Text']['small_font'].width(price_text)
            scrap_width = self.e['Assets'].images['misc']['scrap'].get_width()
            price_width = text_width + scrap_width + 2
            self.e['Text']['small_font'].renderzb(f'{self.price:,}', (self.pos[0] - self.e['Game'].camera[0] - price_width / 2 + scrap_width + 2, self.pos[1] - self.e['Game'].camera[1] - 34 + math.cos(self.e['Window'].time * 1.2 + 0.1 * self.pos[0]) * 4.5), color=(254, 252, 211), bgcolor=(38, 27, 46), z=300)
            self.e['Renderer'].blit(self.e['Assets'].images['misc']['scrap'], (self.pos[0] - self.e['Game'].camera[0] - price_width / 2, self.pos[1] - self.e['Game'].camera[1] - 35 + math.cos(self.e['Window'].time * 1.2 + 0.1 * self.pos[0]) * 4.5), group='default', z=300)
        self.e['Renderer'].blit(img, (self.pos[0] - self.e['Game'].camera[0] - img.get_width() // 2, self.pos[1] - self.e['Game'].camera[1] - img.get_height() // 2 - 16 + math.cos(self.e['Window'].time * 1.2 + 0.1 * self.pos[0]) * 4.5), group='default', z=self.pos[1] / self.e['Tilemap'].tile_size)
        self.e['Renderer'].blit(shadow_img, (self.pos[0] - self.e['Game'].camera[0] - shadow_img.get_width() // 2, self.pos[1] - self.e['Game'].camera[1] - shadow_img.get_height() // 2 + 3), group='default', z=-20)

class State(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.reset()

        save_file = pp.utils.io.read_json('save/save.json')
        self.record = save_file['best_score']
        self.weapon_enchants = save_file['weapon_enchants']
        try:
            self.tutorial_progress = [save_file['tutorial_progress'], save_file['tutorial_controller_progress']]
        except KeyError:
            self.tutorial_progress = [0, 0]

        try:
            self.guide_progress = save_file['guide_progress']
            for field in DEFAULT_SAVE['guide_progress']:
                if field not in self.guide_progress:
                    self.guide_progress[field] = 0
        except KeyError:
            self.guide_progress = {
                'enchant_purchase': 0,
                'weapon_purchase': 0,
                'upgrade_purchase': 0,
                'daisy_talked': 0,
            }

        try:
            self.catalog = save_file['catalog']
            for field in DEFAULT_SAVE['catalog']:
                if field not in self.catalog:
                    self.catalog[field] = []
        except KeyError:
            self.catalog = {
                'weapons': [],
                'enchantments': [],
                'upgrades': [],
                'machines': [],
                'powerups': [],
                'automata': [],
            }

        self.pointer_anim = self.e['EntityDB']['misc'].animations['pointer'].copy()
        self.popup_pointer_anim = self.e['EntityDB']['misc'].animations['pointer'].copy()

        self.upgrade_db = UpgradeDB()
    
    def save(self):
        save_data = {
            'best_score': self.record,
            'weapon_enchants': self.weapon_enchants,
            'tutorial_progress': self.tutorial_progress[0],
            'tutorial_controller_progress': self.tutorial_progress[1],
            'guide_progress': self.guide_progress,
            'catalog': self.catalog,
        }
        pp.utils.io.write_json('save/save.json', save_data)

    def reset_save(self):
        pp.utils.io.write_json('save/save.json', DEFAULT_SAVE)
        self.record = DEFAULT_SAVE['best_score']
        self.weapon_enchants = DEFAULT_SAVE['weapon_enchants']
        self.tutorial_progress = [DEFAULT_SAVE['tutorial_progress'], DEFAULT_SAVE['tutorial_controller_progress']]
        self.guide_progress = DEFAULT_SAVE['guide_progress']
        self.catalog = DEFAULT_SAVE['catalog']

    def catalog_log(self, category, item):
        if category in self.catalog:
            if item not in self.catalog[category]:
                self.catalog[category].append(item)
                self.save()
            if category == 'weapons':
                if len(self.catalog[category]) >= len(WEAPON_STATS):
                    self.e['Steamworks'].grant_achievement('gun_hunter')
            if category == 'upgrades':
                if len(self.catalog[category]) >= len(UPGRADE_LIST):
                    self.e['Steamworks'].grant_achievement('upgrade_hunter')
            if self.catalog_completed:
                self.e['Steamworks'].grant_achievement('completionist')

    @property
    def catalog_completed(self):
        return (len(self.catalog['weapons']) >= len(WEAPON_STATS)) and (len(self.catalog['upgrades']) >= len(UPGRADE_LIST)) and (len(self.catalog['enchantments']) >= len(ENCHANTS)) and (len(self.catalog['machines']) >= len(ENEMY_MACHINES)) and (len(self.catalog['automata']) >= len(AUTOMATA_INFO)) and (self.record >= 31)

    @property
    def difficulty_status(self):
        return {
            'bullet_speed': 92 + self.difficulty / 21,
            'pause': SEASON_STATS[self.season]['pause'] * max(2, 5 - self.difficulty / 850),
            'count': SEASON_STATS[self.season]['count'],
            'step': SEASON_STATS[self.season]['step'],
        }

    def reset(self):
        self.wave = 0
        self.score = 0
        self.scrap = 0
        self.potatoes = 0
        self.shopping = 0
        self.ending_shopping = False
        self.shop_upgrades = [None] * 3
        self.owned_upgrades = {upgrade: 0 for upgrade in ALL_SHOP_UPGRADES}
        self.notifications = []
        self.dialogue = [None, []]
        self.dialogue_state = {'progress': 0, 'ui_offset': 60}
        self.closest_entity = [None, 99999]
        # time based difficulty
        self.difficulty = 0
        # chosen difficulty ruleset
        self.difficulty_set = Difficulties.NORMAL
        self.effects = {effect: [0, 0.01] for effect in EFFECTS}
        self.interactables = []
        self.enchanting = False
        self.enchanting_offset = 300
        self.enchanting_selection_index = 0
        self.enchant_anim_progress = 0
        self.enchant_anim_offset = 0
        self.kill_log = []
        self.marker_color = (254, 252, 211)
        if self.e['Game'].player:
            self.e['Game'].player.reset()
        # text, offset, callback, selection_i
        self.popup = [None, 200, None, 0]
        for group in ['enemies', 'frenemies', 'vfx']:
            self.e['EntityGroups'].groups[group] = []
        self.clear_map()

    def log_kill(self):
        self.kill_log.append(0)

    def kills_within(self, duration):
        count = 0
        for kill in self.kill_log:
            if kill <= duration:
                count += 1
        return count

    def upgrade_stat(self, upgrade):
        info = UPGRADE_INFO[upgrade]
        if info['stat_pattern'] == 'exponential':
            return ((1 + info['stat_rate']) ** self.owned_upgrades[upgrade] - 1)
        elif info['stat_pattern'] == 'inverse_exponential':
            return (1 - (1 - info['stat_rate']) ** self.owned_upgrades[upgrade])
        else:
            # linear addition case
            return self.owned_upgrades[upgrade] * info['stat_rate']
        
    def add_potato(self):
        self.potatoes += 1
        self.e['Sounds'].play('pickup', volume=0.5)
        if self.potatoes >= 23:
            self.potatoes -= 23
            effect_type = random.choice(OBTAINABLE_POWERUPS)
            self.e['State'].add_effect(effect_type, ABILITY_DURATIONS[effect_type])
            self.e['Sounds'].play('powerup', volume=0.45)

    @property
    def difficulty_set_stats(self):
        return Difficulties.info(self.difficulty_set)

    @property
    def ui_busy(self):
        return self.e['State'].dialogue[0] or self.enchanting or self.title or self.popup[2] or self.e['PauseMenu'].paused or self.e['PauseMenu'].victory
    
    @property
    def inv_enchanting_offset(self):
        return 300 - self.enchanting_offset
    
    @property
    def left_inv_offset(self):
        if self.inv_enchanting_offset:
            return self.inv_enchanting_offset
        elif self.e['PauseMenu'].pause_offset != 200:
            return 200 - self.e['PauseMenu'].pause_offset
        return 0
    
    @property
    def right_inv_offset(self):
        return self.left_inv_offset

    @property
    def season(self):
        wave = self.wave

        # new areas start with shopping area
        if (self.shopping > 1) or self.ending_shopping:
            wave += 1
        
        if wave > 0:
            wave = ((wave - 1) % 40) + 1

        if wave <= 10:
            return 'summer'
        elif wave <= 20:
            return 'fall'
        elif wave <= 30:
            return 'winter'
        else:
            self.e['Sounds'].sounds['ambience'].set_volume(0)
            return 'void'

    def clear_map(self):
        if 'enemies' in self.e['EntityGroups'].groups:
            for entity in self.e['EntityGroups'].groups['enemies']:
                if type(entity) == CentipedeRig:
                    entity.damage(entity.health)
        if 'minions' in self.e['EntityGroups'].groups:
            self.e['EntityGroups'].groups['minions'] = []
        if 'entities' in self.e['EntityGroups'].groups:
            for entity in list(self.e['EntityGroups'].groups['entities']):
                if entity.type != 'player':
                    self.e['EntityGroups'].groups['entities'].remove(entity)
        if 'frenemies' in self.e['EntityGroups'].groups:
            for frenemy in list(self.e['EntityGroups'].groups['frenemies']):
                if (not frenemy.friendly) or (frenemy.camping):
                    self.e['EntityGroups'].groups['frenemies'].remove(frenemy)
                else:
                    frenemy.revived = False
        if self.e['Game'].player:
            if self.e['Game'].player.weapon:
                self.e['Game'].player.weapon.reset()
            if self.e['Game'].player.alt_weapon:
                self.e['Game'].player.alt_weapon.reset()
        self.interactables = []

    def load_title(self):
        self.title = True
        self.e['Tilemap'].load_map('fortress')
        self.e['Music'].fadeout(0.5)
        self.e['Sounds'].sounds['ambience'].set_volume(self.e['Settings'].sfx_volume * 0.6)
        self.e['Menus'].submenu = 'title'
        self.e['Music'].play('menu')

    def effect_active(self, effect_id):
        return self.effects[effect_id][0]
    
    def clear_effect(self, effect_id):
        if effect_id in self.effects:
            self.effects[effect_id] = [0, 0.01]

    def add_effect(self, effect_id, duration, hidden=False):
        self.catalog_log('powerups', effect_id)

        if effect_id in COOLDOWN_EFFECTS:
            duration *= (1 - self.e['State'].upgrade_stat('charged_coffee'))

        if not hidden:
            self.notify(f'+{EFFECTS[effect_id]}', font='small_font')
        if effect_id == 'potion':
            self.e['Game'].player.heal(2)
            return
        if effect_id == 'shield':
            self.e['Game'].player.shield = min(self.e['Game'].player.shield + 1, self.e['Game'].player.max_health)
            self.e['Sounds'].play('shield_applied', volume=1.0)
            return
        if effect_id == 'freeze':
            self.e['Sounds'].play('long_freeze', volume=1.0)
        if duration > self.effects[effect_id][0]:
            self.effects[effect_id] = [duration, duration]

    def notify(self, text, font='large_font'):
        self.notifications.append([text, self.e['Game'].display.get_height(), 3, font])

    def shop(self):
        if not self.shopping:
            self.shopping = 1
        self.e['Game'].player.shop_landed = False
        self.e['Transition'].end_level(self.shop_land)

    def load_area(self, area_id):
        self.clear_map()

        self.e['Tilemap'].load_map(area_id)

        if self.wave or (not self.e['Tilemap'].respawn):
            self.e['Game'].player.pos = list(self.e['Tilemap'].spawn)
            self.e['Game'].player.height = 200
        else:
            self.e['Game'].player.pos = list(self.e['Tilemap'].respawn)
            self.e['Game'].player.height = 0

        if self.e['Game'].player.partner[0]:
            self.e['Game'].player.partner[0].pos = [self.e['Game'].player.pos[0] + 3, self.e['Game'].player.pos[0] - 4]
            self.e['Game'].player.partner[0].height = self.e['Game'].player.height
            self.e['Game'].player.partner[0].health = self.e['Game'].player.partner[0].max_health

        self.e['Machines'].minimap = self.e['Tilemap'].minimap_base.copy()
        self.e['Machines'].minimap.set_alpha(180)

    def final_boss(self):
        self.wave -= 1
        self.e['Machines'].new_wave(boss=True)

    def shop_land(self):
        # clear effects (important for miasma)
        self.effects = {effect: [0, 0.01] for effect in EFFECTS}
        # clear shield
        self.e['Game'].player.shield = 0

        self.shopping = 2

        if self.season == 'fall':
            self.e['Music'].play('fall_shop', start=self.e['Window'].time, fadein=2.5)
        elif self.season == 'winter':
            self.e['Music'].play('winter_shop', start=self.e['Window'].time, fadein=2.5)
        elif self.season == 'void':
            self.e['Music'].play('void_shop', start=self.e['Window'].time, fadein=2.5)
        else:
            self.e['Music'].play('summer_shop', start=self.e['Window'].time, fadein=2.5)
        self.load_area(f'{self.e["State"].season}_transition')

        if self.wave:
            self.notify('Buy Phase')
        self.e['Sounds'].play('shop', volume=0.4)
        
        if self.wave > self.record:
            self.record = self.wave
            self.save()

        if self.record >= 10:
            self.e['Steamworks'].grant_achievement('time_flies')

        self.upgrade_db.compute_weights()
        for i, shop in enumerate(self.e['Tilemap'].shops):
            shop_pos = shop[0]
            shop_type = shop[1]
            item = self.upgrade_db.shop_select()
            if self.wave != 0:
                price = calc_price(UPGRADE_INFO[item]['base_price'] * PRICE_SCALE['upgrade'], self.owned_upgrades[item])
                guide = False
                if (not self.guide_progress['upgrade_purchase']) and (self.scrap >= 10) and (i == 0):
                    item = 'shockwave'
                    price = 10
                    guide = True
                if shop_type == 'alt_shop':
                    price *= ALT_SHOP_PREMIUM
                self.interactables.append(Interactable('shop', item, (shop_pos[0] + self.e['Tilemap'].tile_size * 0.5, shop_pos[1] + self.e['Tilemap'].tile_size * 0.5), int(price), guide=guide))
        for i, shop_pos in enumerate(self.e['Tilemap'].weapon_shops):
            weapon = random.choice(self.weapons_available)
            if self.wave != 0:
                price = UPGRADE_INFO[weapon]['base_price'] * PRICE_SCALE['weapon']
                guide = False
                if DEMO:
                    price = int(price * 0.5)
                if self.guide_progress['upgrade_purchase'] and self.guide_progress['daisy_talked'] and self.guide_progress['enchant_purchase'] and (not self.guide_progress['weapon_purchase']):
                    weapon = 'beamer'
                    if (self.wave > 3) and (self.scrap >= 25) and (i == 0):
                        guide = True
                        price = 25
                self.interactables.append(Interactable('weapon', weapon, (shop_pos[0] + self.e['Tilemap'].tile_size * 0.5, shop_pos[1] + self.e['Tilemap'].tile_size * 0.5), int(price), guide=guide))
        
        self.interactables.append(Interactable('next', 'next', self.e['Tilemap'].exit))

    @property
    def weapons_available(self):
        weapon_list = []
        for weapon in WEAPON_STATS:
            if 'minimum_wave' in WEAPON_STATS[weapon]:
                if WEAPON_STATS[weapon]['minimum_wave'] > self.wave:
                    continue
            weapon_list.append(weapon)
        return weapon_list

    def end_shopping(self):
        self.shopping = 0
        self.ending_shopping = True
        self.e['Transition'].end_level(self.e['Machines'].new_wave)

    def challenge_callback(self, result):
        if result:
            self.e['Transition'].end_level(self.final_boss)
        else:
            self.e['State'].shop()

    def update(self):
        if (not (self.shopping or self.ui_busy)) and self.e['Machines'].active_enemies_remaining:
            self.difficulty += self.e['Window'].dt

        self.marker_color = (254, 252, 211)
        if self.season in {'winter', 'void'}:
            self.marker_color = (191, 60, 96)

        for i, kill in enumerate(self.kill_log):
            self.kill_log[i] += self.e['Window'].dt
        while len(self.kill_log) and self.kill_log[0] > 10:
            self.kill_log.pop(0)
        if self.e['State'].upgrade_stat('rampage') and (self.kills_within(1) >= 8):
            if not self.e['State'].effect_active('rampage'):
                self.e['Game'].player.weapon.secondary_cooldown[0] = 0
                self.e['State'].add_effect('rampage', 16)
                self.e['Sounds'].play('rampage', volume=1.0)

        for effect in self.effects:
            self.effects[effect][0] = max(0, self.effects[effect][0] - self.e['Window'].dt)
            if not self.effects[effect][0]:
                self.effects[effect][1] = 0.01

        for notification in self.notifications[::-1]:
            if notification[2] >= 0:
                notification[1] += (60 - notification[1]) * 3 * self.e['Window'].dt
            else:
                notification[1] += (-80 - notification[1]) * 3 * self.e['Window'].dt
            notification[2] -= self.e['Window'].dt
            if notification[2] < -2:
                self.notifications.remove(notification)

    def render_ability_cooldown(self, ability, pos, z=9999, group='default'):
        if self.e['Game'].player.weapon and (WEAPON_STATS[self.e['Game'].player.weapon.type]['primary'] == ability):
            cooldown_ratio = self.e['Game'].player.weapon.shoot_cooldown[0] / self.e['Game'].player.weapon.shoot_cooldown[1]
            input_name = ('shoot', 'primary')
        elif ability == 'swap':
            cooldown_ratio = self.e['Game'].player.swap_cooldown / self.e['Game'].player.swap_cooldown_amt
            input_name = ('swap_weapon', 'swap')
        elif ability == 'dodge':
            cooldown_ratio = self.e['Game'].player.roll_cooldown / self.e['Game'].player.roll_cooldown_amt
            input_name = ('dodge', 'dodge')
        else:
            cooldown_ratio = self.e['Game'].player.weapon.secondary_cooldown[0] / self.e['Game'].player.weapon.secondary_cooldown[1]
            input_name = ('secondary', 'secondary')
        if self.e['Game'].controller_mode:
            input_tip_img = self.e['InputTips'].lookup_controller_binding(self.e['Controllers'].inv_name_mapping[input_name[1]])
        else:
            input_tip_img = self.e['InputTips'].lookup_binding(self.e['Input'].config[input_name[0]], tiny=True)
        cooldown_ratio = max(0, min(1, cooldown_ratio))
        img = self.e['Assets'].images['upgrades'][f'{ability}_b'].copy()
        if not cooldown_ratio:
            self.e['Renderer'].blit(img, pos, z=z, group=group)
        else:
            img.set_alpha(80)
            self.e['Renderer'].blit(img, pos, z=z, group=group)
            img.blit(pygame.Surface((img.get_width(), int((cooldown_ratio * 0.75 + 0.125) * img.get_height()))), (0, 0))
            self.e['Renderer'].blit(img, pos, z=z, group=group)
            self.e['Renderer'].blit(self.e['Assets'].images['upgrades']['frame'], pos, z=z, group=group)
        self.e['InputTips'].render_icon(input_tip_img, (pos[0] + 4 + self.e['State'].right_inv_offset - input_tip_img.get_width(), pos[1] + 11), z=9999, group='ui')

    def strip_enchant_callback(self, response):
        if response:
            self.e['Game'].player.weapon.strip()
            self.e['Sounds'].play('strip_enchant', volume=1.0)
        self.e['Sounds'].play('tap')

    @property
    def interacted(self):
        return self.e['Input'].pressed('interact') or (self.e['Game'].controller_mode and self.e['Controllers'].pressed('interact'))
    
    def render_weapon_enchants(self, weapon, offset=(0, 0), z_offset=0):
        if len(weapon.enchant_list):
            for i, enchant in enumerate(weapon.enchant_list):
                self.e['Text']['small_font'].renderzb(f'{ENCHANTS[enchant[1]]["name"]} {roman_numeral(int(math.ceil(enchant[2] * enchant[0])))}', (4 - offset[0], 62 + 26 * i - offset[1]), color=(191, 60, 96), bgcolor=(38, 27, 46), z=9998 + z_offset, group='ui')
                self.e['Text']['small_font'].renderzb(ENCHANTS[enchant[1]]['text'].replace('<stat>', str(nice_round(weapon.enchant_stat(enchant[1]) * 100, 1))), (4 - offset[0], 72 + 26 * i - offset[1]), color=(163, 179, 182), bgcolor=(38, 27, 46), z=9998 + z_offset, group='ui')
        else:
            self.e['Text']['small_font'].renderzb('No active enchantments...', (4 - offset[0], 62 - offset[1]), color=(121, 132, 157), bgcolor=(38, 27, 46), z=9998 + z_offset, group='ui')

    def render_weapon_enchants_compressed(self, weapon, offset=(0, 0), z=9999):
        if len(weapon.enchant_list):
            y_offset = 0
            for i, enchant in enumerate(weapon.enchant_list):
                self.e['Text']['small_font'].renderzb(f'{ENCHANTS[enchant[1]]["name"]} {roman_numeral(int(math.ceil(enchant[2] * enchant[0])))}', (offset[0], y_offset + offset[1]), color=(191, 60, 96), bgcolor=(38, 27, 46), z=z, group='ui')
                desc_prep = self.e['Text']['small_font'].prep_text(ENCHANTS[enchant[1]]['text'].replace('<stat>', str(nice_round(weapon.enchant_stat(enchant[1]) * 100, 1))), line_width=132)
                desc_height = desc_prep.height
                self.e['Text']['small_font'].renderzb(desc_prep.text, (offset[0], 10 + y_offset + offset[1]), color=(163, 179, 182), bgcolor=(38, 27, 46), z=z, group='ui')
                y_offset += desc_height + 12
        else:
            self.e['Text']['small_font'].renderzb('No active enchantments...', offset, color=(121, 132, 157), bgcolor=(38, 27, 46), z=z, group='ui')


    def purchase_event(self, upgrade):
        player = self.e['Game'].player
        self.catalog_log('upgrades', upgrade)
        if upgrade == 'heart':
            player.max_health += 1
            player.heal(1)
        if upgrade == 'all_natural':
            player.max_health += 4
            player.heal(4)
        if upgrade == 'potion':
            player.heal((player.max_health - player.health) * 0.2 + 2)
        elif upgrade == 'overstocked':
            if player.partner[0]:
                player.partner[0].weapon = Weapon(random.choice(list(WEAPON_STATS)), player.partner[0])
        elif upgrade == 'mystery_item':
            new_upgrade = self.e['UpgradeDB'].true_random_select(exclude=['mystery_item'])
            self.notify(f'+{UPGRADE_INFO[new_upgrade]["name"]}', font='small_font')
            self.purchase_event(new_upgrade)
        else:
            self.owned_upgrades[upgrade] += 1

    def render(self):
        if self.shopping > 1:
            nearby_item = None

            for interactable in self.interactables:
                interactable.render()
                interactable_range = 12
                if interactable.type == 'next':
                    interactable_range = 18
                if interactable.dis < interactable_range:
                    nearby_item = interactable

            if not self.ui_busy:
                if nearby_item:
                    self.e['Text']['small_font'].renderzb(UPGRADE_INFO[nearby_item.type]['name'], (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width(UPGRADE_INFO[nearby_item.type]['name']) / 2, 150 + math.cos(self.e['Window'].time * 2) * 2.5), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
                    upgrade_desc = generate_description(nearby_item.type, 1)
                    self.e['Text']['small_font'].renderzb(upgrade_desc, (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width(upgrade_desc) / 2, 166 + math.cos(self.e['Window'].time * 1.7) * 2.5), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
                    if nearby_item.category == 'next':
                        self.e['Text']['small_font'].renderzb('to proceed', (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width('to proceed') / 2 + 6, 182), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
                        self.e['InputTips'].render_icon(self.e['InputTips'].interact_icon, (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width('to proceed') / 2 - 6, 180), group='ui', z=9998)
                        if self.interacted:
                            self.e['Sounds'].play('tap')
                            for j in range(25):
                                self.e['EntityGroups'].add(pp.vfx.Spark((nearby_item.pos[0], nearby_item.pos[1] - 16 + math.cos(self.e['Window'].time * 1.2 + 0.1 * nearby_item.pos[0]) * 4.5), random.random() * math.pi * 2, size=(random.randint(6, 10), random.randint(1, 2)), speed=random.random() * 60 + 60, decay=random.random() * 4 + 2, color=(254, 252, 211), z=300), 'vfx')
                            self.end_shopping()
                            if self.e['Tutorial'].state == 4:
                                self.e['Tutorial'].advance()
                    elif nearby_item.price <= self.scrap:
                        self.e['Text']['small_font'].renderzb('to buy', (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width('to buy') / 2 + 6, 182), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
                        self.e['InputTips'].render_icon(self.e['InputTips'].interact_icon, (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width('to buy') / 2 - 6, 180), group='ui', z=9998)
                        if self.interacted:
                            if (nearby_item.type == 'potion') and (self.e['Game'].player.health == self.e['Game'].player.max_health):
                                self.e['Sounds'].play('denied', 0.5)
                                self.e['State'].notify('Already at full health!', font='small_font')
                            else:
                                self.e['Sounds'].play('jingle')
                                self.scrap -= nearby_item.price
                                player = self.e['Game'].player
                                if nearby_item.category == 'shop':
                                    self.purchase_event(nearby_item.type)
                                    if not self.guide_progress['upgrade_purchase']:
                                        self.guide_progress['upgrade_purchase'] = 1
                                        self.save()
                                elif nearby_item.category == 'weapon':
                                    if not player.alt_weapon:
                                        player.alt_weapon = Weapon(nearby_item.type, player)
                                    else:
                                        player.weapon = Weapon(nearby_item.type, player)
                                    if not self.guide_progress['weapon_purchase']:
                                        self.guide_progress['weapon_purchase'] = 1
                                        self.save()
                                
                                self.interactables.remove(nearby_item)
                                for j in range(25):
                                    self.e['EntityGroups'].add(pp.vfx.Spark((nearby_item.pos[0], nearby_item.pos[1] - 16 + math.cos(self.e['Window'].time * 1.2 + 0.1 * nearby_item.pos[0]) * 4.5), random.random() * math.pi * 2, size=(random.randint(6, 10), random.randint(1, 2)), speed=random.random() * 60 + 60, decay=random.random() * 4 + 2, color=(254, 252, 211), z=300), 'vfx')
                    elif self.interacted:
                        self.e['Sounds'].play('denied', 0.5)
                elif self.closest_entity[0]:
                    action_name = 'interact'
                    if self.closest_entity[0].type in FRENEMY_LEVELS:
                        action_name = 'recruit'
                    self.e['Text']['small_font'].renderzb(f'to {action_name}', (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width(f'to {action_name}') / 2 + 6, 182), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
                    self.e['InputTips'].render_icon(self.e['InputTips'].interact_icon, (self.e['Game'].display.get_width() / 2 - self.e['Text']['small_font'].width(f'to {action_name}') / 2 - 6, 180), group='ui', z=9998)
                    if self.interacted:
                        self.closest_entity[0].interact()
            
        if self.dialogue[0]:
            fresh = not self.dialogue_state['progress']
            z_offset = 0
            if self.e['PauseMenu'].victory:
                z_offset = 500
            if not len(self.dialogue[1]):
                # dialogue hide animation
                self.dialogue_state['ui_offset'] += (60 - self.dialogue_state['ui_offset']) * self.e['Window'].dt * 10
            else:
                self.dialogue_state['ui_offset'] += (0 - self.dialogue_state['ui_offset']) * self.e['Window'].dt * 10
                if self.dialogue_state['ui_offset'] < 0.5:
                    self.dialogue_state['ui_offset'] = 0
                if self.dialogue_state['ui_offset'] < 10:
                    last_progress = self.dialogue_state['progress']
                    self.dialogue_state['progress'] += self.e['Window'].dt
                    msg = self.dialogue[1][0]
                    if msg[:5] == '<img>':
                        msg = msg.split('<text>')[-1]
                    if self.dialogue[0].type != 'goat':
                        if (last_progress % (1 / 30)) > (self.dialogue_state['progress'] % (1 / 30)):
                            if int(self.dialogue_state['progress'] * 30) < len(msg):
                                char = self.dialogue[1][0][int(self.dialogue_state['progress'] * 30)]
                                if char.lower() in {' ', ',', '.', '!', '?', '-', 'a', 'e', 'i', 'o', 'u', 'h'}:
                                    self.e['Sounds'].play(f'{self.dialogue[0].type}_voice', volume=0.15)
                                else:
                                    self.e['Sounds'].play(f'{self.dialogue[0].type}_voice', volume=0.3)
            portrait_img = self.e['Assets'].images['portraits'][self.dialogue[0].type]
            self.e['Renderer'].blit(portrait_img, (5 - self.dialogue_state['ui_offset'], self.e['Game'].display.get_height() - 5 - portrait_img.get_height()), group='ui', z=9998.5 + z_offset)
            self.e['Renderer'].blit(self.e['Assets'].images['misc']['portrait_frame'], (3 - self.dialogue_state['ui_offset'], self.e['Game'].display.get_height() - 7 - portrait_img.get_height()), group='ui', z=9998.6 + z_offset)
            self.e['Text']['small_font'].renderzb(self.dialogue[0].name, (50, self.e['Game'].display.get_height() - 5 - portrait_img.get_height() + self.dialogue_state['ui_offset']), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998.5 + z_offset, group='ui')

            banner_bg = pygame.Surface((self.e['Game'].display.get_width(), 10 + portrait_img.get_height()), pygame.SRCALPHA)
            banner_bg.fill((38, 27, 46, 110))
            self.e['Renderer'].blit(banner_bg, (0, self.e['Game'].display.get_height() - banner_bg.get_height() + self.dialogue_state['ui_offset']), group='ui', z=9998.4 + z_offset)

            if len(self.dialogue[1]):
                msg = self.dialogue[1][0]
                img = None
                if msg[:5] == '<img>':
                    img = self.e['Assets'].images['misc'][msg[5:].split('<')[0]]
                    offset = max(0, (0.5 - self.dialogue_state['progress']) * 120) ** 1.5
                    self.e['Renderer'].blit(img, (self.e['Game'].display.get_width() / 2 - img.get_width() / 2, self.e['Game'].display.get_height() / 2 - img.get_height() / 2 + offset - 10), group='ui', z=9998.9 + z_offset)
                    msg = msg.split('<text>')[-1]
                self.e['Text']['small_font'].renderzb(msg[:int(self.dialogue_state['progress'] * 30)], (50, self.e['Game'].display.get_height() + 7 - portrait_img.get_height() + self.dialogue_state['ui_offset']), line_width=self.e['Game'].display.get_width() - 70, color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998.5 + z_offset, group='ui')
                if self.interacted and (not fresh):
                    if img and (self.dialogue_state['progress'] >= 0.5):
                        self.dialogue[1].pop(0)
                        self.dialogue_state['progress'] = 0
                    elif int(self.dialogue_state['progress'] * 30) >= len(msg):
                        self.dialogue[1].pop(0)
                        self.dialogue_state['progress'] = 0
                        if len(self.dialogue[1]) and (self.dialogue[1][0][:5] == '<img>'):
                            self.e['Sounds'].play('ui_slide', volume=0.3)
                    else:
                        self.dialogue_state['progress'] = len(msg) / 30
                    self.e['Sounds'].play('tap')
                if int(self.dialogue_state['progress'] * 30) >= len(msg):
                    self.e['InputTips'].render_icon(self.e['InputTips'].interact_icon, (self.e['Game'].display.get_width() - self.e['InputTips'].interact_icon.get_width() - 4, self.e['Game'].display.get_height() - self.e['InputTips'].interact_icon.get_height() - 4 + (1 if self.e['Window'].time % 1 < 0.25 else 0)), group='ui', z=9998.5 + z_offset)
            else:
                if self.dialogue_state['ui_offset'] > 55:
                    if self.dialogue[0].type == 'gary':
                        self.enchanting = True
                        self.e['Sounds'].play('ui_slide', volume=0.35)
                    # fully ends dialogue state
                    self.dialogue = [None, []]
                    self.dialogue_state['progress'] = 0

        self.pointer_anim.update(self.e['Window'].dt)
        self.popup_pointer_anim.update(self.e['Window'].dt)

        if self.enchanting:
            self.enchanting_offset += -self.enchanting_offset * self.e['Window'].dt * 5
            if self.enchanting_offset < 0.7:
                self.enchanting_offset = 0
        else:
            self.enchanting_offset += (300 - self.enchanting_offset) * self.e['Window'].dt * 9
            if self.enchanting_offset > 299.3:
                self.enchanting_offset = 300
        if self.enchanting_offset < 290:
            if self.e['Input'].pressed('pause') or self.e['Controllers'].pressed('back'):
                self.enchanting = False
                self.e['Input'].consume('pause')
            weapon = self.e['Game'].player.weapon
            if self.enchant_anim_progress:
                self.enchant_anim_progress += self.e['Window'].dt
                if self.enchant_anim_progress > 2.5:
                    self.enchant_anim_progress = 0
                    self.enchant_anim_offset = 0
                elif self.enchant_anim_progress > 1.34:
                    self.enchant_anim_offset += -self.enchant_anim_offset * self.e['Window'].dt * 9
                    if self.enchant_anim_progress - self.e['Window'].dt <= 1.34:
                        # enchant when the animation reverses direction to reveal the enchant
                        weapon.enchant()
                        if len(weapon.enchant_list):
                            for i, enchant in enumerate(weapon.enchant_list):
                                self.e['EntityGroups'].add(Slash((0, 65 + 26 * i), 0, (7, 7), color=(254, 252, 211), speed=11, decay=40, group='ui', z=9999.5), 'vfx')
                                self.e['EntityGroups'].add(Slash((0, 75 + 26 * i), 0, (10, 7), color=(254, 252, 211), speed=14, decay=40, group='ui', z=9999.5), 'vfx')
                                self.e['EntityGroups'].add(Slash((0, 65 + 26 * i), 0, (9, 9), color=(38, 27, 46), speed=11, decay=35, group='ui', z=9999.4), 'vfx')
                                self.e['EntityGroups'].add(Slash((0, 75 + 26 * i), 0, (12, 9), color=(38, 27, 46), speed=14, decay=35, group='ui', z=9999.4), 'vfx')
                else:
                    self.enchant_anim_offset += (300 - self.enchant_anim_offset) * self.e['Window'].dt * 5
            self.e['Renderer'].blit(self.e['Assets'].images['misc']['full_fade'], (-self.enchanting_offset, 0), z=9980, group='ui')
            self.e['Text']['large_font'].renderzb('Blacksmith Enchant', (4 - self.e['State'].enchanting_offset, 4), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
            self.e['Text']['small_font'].renderzb(weapon.title, (4 - self.e['State'].enchanting_offset, 33), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')
            weapon_img = self.e['Assets'].images['weapons'][f'{weapon.type}_icon']
            self.e['Renderer'].blit(weapon_img, (4 - self.e['State'].enchanting_offset, 41), z=9998, group='ui')
            self.e['Renderer'].blit(self.e['Assets'].images['weapons'][f'{weapon.type}_flat'], (8 - self.e['State'].enchanting_offset, 44), z=9997, group='ui')
            self.e['Game'].player.weapon.render_stars((4 - self.e['State'].enchanting_offset, 41 + weapon_img.get_height() - 3), group='ui', z=9999)
            self.e['Renderer'].blit(self.e['Assets'].images['misc']['scrap'], (4 - self.e['State'].enchanting_offset, 21), z=9998, group='ui')
            self.e['Text']['small_font'].renderzb(f'{self.scrap:,}', (13 - self.e['State'].enchanting_offset, 22), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')

            
            self.render_weapon_enchants(weapon, offset=(self.enchanting_offset + self.enchant_anim_offset, 0))

            enchanting_options = ['Back', 'Strip Enchants', 'Enhance']
            if not len(weapon.enchant_list):
                enchanting_options = ['Back', 'Enchant']

            if (not self.popup[2]):
                if self.e['Controllers'].nav_pressed('move_y', 'move_x') or self.e['Controllers'].pressed('menu_down'):
                    self.enchanting_selection_index = (self.enchanting_selection_index - 1) % len(enchanting_options)
                    self.pointer_anim.reset()
                    self.e['Sounds'].play('tap')
                if self.e['Controllers'].nav_pressed_neg('move_y', 'move_x') or self.e['Controllers'].pressed('menu_up'):
                    self.enchanting_selection_index = (self.enchanting_selection_index + 1) % len(enchanting_options)
                    self.pointer_anim.reset()
                    self.e['Sounds'].play('tap')
            
            for i, option in enumerate(enchanting_options):
                if i == self.enchanting_selection_index:
                    self.e['Renderer'].blit(self.pointer_anim.img, (3 - self.e['State'].enchanting_offset, self.e['Game'].display.get_height() - 12 * (i + 2) - 1), z=9998, group='ui')
                option_r = pygame.Rect(-self.e['State'].enchanting_offset, self.e['Game'].display.get_height() - 12 * (i + 2) - 2, 70, 10)
                hovering = option_r.collidepoint(self.e['Game'].mpos) or self.e['Game'].controller_mode
                text_offset = 0
                if hovering and (not self.popup[2]):
                    if not self.e['Game'].controller_mode:
                        if self.enchanting_selection_index != i:
                            self.enchanting_selection_index = i
                            self.pointer_anim.reset()
                            self.e['Sounds'].play('tap')
                    if self.enchanting_selection_index == i:
                        if (self.e['Input'].pressed('shoot') or self.e['Controllers'].pressed('interact')) and (not self.enchant_anim_progress):
                            self.e['Input'].consume('shoot')
                            self.e['Controllers'].consume('interact')
                            self.e['Sounds'].play('tap')
                            if option == 'Back':
                                self.enchanting = False
                            if option in ['Enchant', 'Enhance']:
                                if self.scrap >= weapon.enchant_price:
                                    self.scrap -= weapon.enchant_price
                                    self.e['Sounds'].play('enchant', volume=1.0)
                                    self.enchant_anim_progress = 0.01
                                else:
                                    self.e['Sounds'].play('denied', 0.5)
                            if option == 'Strip Enchants':
                                self.popup = ['Are you sure you want to strip all enchants?', 200, self.strip_enchant_callback, 0]
                        text_offset = math.sin(self.e['Window'].time * 9) * 2.5 + 2.5
                if option in ['Enchant', 'Enhance']:
                    self.e['Renderer'].blit(self.e['Assets'].images['misc']['scrap'], (46 - self.e['State'].enchanting_offset + text_offset, self.e['Game'].display.get_height() - 12 * (i + 2) - 1), z=9998, group='ui')
                    color = (254, 252, 211)
                    if self.scrap < weapon.enchant_price:
                        color = (191, 60, 96)
                    self.e['Text']['small_font'].renderzb(str(weapon.enchant_price), (54 - self.e['State'].enchanting_offset + text_offset, self.e['Game'].display.get_height() - 12 * (i + 2)), color=color, bgcolor=(38, 27, 46), z=9998, group='ui')
                self.e['Text']['small_font'].renderzb(option, (14 - self.e['State'].enchanting_offset + text_offset, self.e['Game'].display.get_height() - 12 * (i + 2)), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')

        if self.popup[0]:
            if self.popup[2]:
                if self.e['Controllers'].nav_pressed('move_x', 'move_y') or self.e['Controllers'].nav_pressed_neg('move_x', 'move_y') or self.e['Controllers'].pressed('menu_right') or self.e['Controllers'].pressed('menu_left'):
                    self.popup[3] = 1 - self.popup[3]
                    self.popup_pointer_anim.reset()
                    self.e['Sounds'].play('tap')
            if self.popup[2]:
                self.popup[1] += -self.popup[1] * self.e['Window'].dt * 10
            else:
                self.popup[1] += (200 - self.popup[1]) * self.e['Window'].dt * 10
            popup_bg = self.e['Assets'].images['misc']['popup_bg']
            popup_tl = (self.e['Game'].display.get_width() / 2 - popup_bg.get_width() / 2, self.e['Game'].display.get_height() / 2 - popup_bg.get_height() / 2 + self.popup[1])
            self.e['Renderer'].blit(popup_bg, popup_tl, z=9999, group='ui')

            popup_text = self.popup[0]

            if len(self.popup) >= 6:
                self.popup[5] = max(0, self.popup[5] - self.e['Window'].dt)
                if self.popup[2] and (not self.popup[5]):
                    old_popup = self.popup[2]
                    self.popup[2](False)
                    if self.popup[2] == old_popup:
                        self.popup[2] = None
                
                popup_text = popup_text.replace('[TIMER]', str(math.ceil(self.popup[5])))

            self.e['Text']['small_font'].renderzb(popup_text, (popup_tl[0] + 5, popup_tl[1] + 5), color=(254, 252, 211), bgcolor=(38, 27, 46), line_width=popup_bg.get_width() - 10, z=9999.5, group='ui')

            options = ['No', 'Yes']
            if len(self.popup) >= 5:
                options = self.popup[4]

            for i, option in enumerate(options):
                option_width = self.e['Text']['small_font'].width(option)
                option_pos = (popup_tl[0] + 30 - option_width / 2 + i * (popup_bg.get_width() - 30 * 2), popup_tl[1] + popup_bg.get_height() - 11)
                if i == self.popup[3]:
                    self.e['Renderer'].blit(self.popup_pointer_anim.img, (option_pos[0] - 10, option_pos[1] - 1), z=9999.5, group='ui')
                option_r = pygame.Rect(option_pos[0] - 4, option_pos[1] - 2, option_width + 4, 12)
                hovering = option_r.collidepoint(self.e['Game'].mpos) or self.e['Game'].controller_mode
                text_offset = 0
                if hovering and self.popup[2]:
                    if not self.e['Game'].controller_mode:
                        if self.popup[3] != i:
                            self.popup[3] = i
                            self.popup_pointer_anim.reset()
                            self.e['Sounds'].play('tap')
                    if self.popup[3] == i:
                        if (self.e['Input'].pressed('shoot') or self.e['Controllers'].pressed('interact')):
                            self.e['Input'].consume('shoot')
                            self.e['Controllers'].consume('interact')
                            self.e['Sounds'].play('tap')
                            old_popup = self.popup[2]
                            self.popup[2](i == 1)
                            if self.popup[2] == old_popup:
                                self.popup[2] = None
                        text_offset = math.sin(self.e['Window'].time * 9) * 2.5 + 2.5
                self.e['Text']['small_font'].renderzb(option, (option_pos[0] + text_offset, option_pos[1]), color=(254, 252, 211), bgcolor=(38, 27, 46), line_width=popup_bg.get_width() - 10, z=9999.5, group='ui')
            
        if (not (self.e['Game'].player.dead or self.e['Transition'].progress or self.e['Transition'].level_end or self.ui_busy)) or (self.e['State'].right_inv_offset):
            if not self.e['HUD'].hide_ui:
                self.render_ability_cooldown(WEAPON_STATS[self.e['Game'].player.weapon.type]['primary'], (self.e['Game'].display.get_width() - 40 + self.e['State'].right_inv_offset, self.e['Game'].display.get_height() - 22), z=9998, group='ui')
                self.render_ability_cooldown(WEAPON_STATS[self.e['Game'].player.weapon.type]['secondary'], (self.e['Game'].display.get_width() - 20 + self.e['State'].right_inv_offset, self.e['Game'].display.get_height() - 22), z=9998, group='ui')
                self.render_ability_cooldown('dodge', (self.e['Game'].display.get_width() - 60 + self.e['State'].right_inv_offset, self.e['Game'].display.get_height() - 22), z=9998, group='ui')
                if self.e['Game'].player.alt_weapon:
                    self.render_ability_cooldown('swap', (self.e['Game'].display.get_width() - 80 + self.e['State'].right_inv_offset, self.e['Game'].display.get_height() - 22), z=9998, group='ui')

            # 10 is upper padding and the bottom 27 are for cooldowns
            right_side_remaining_vertical = self.e['Game'].display.get_height() - (self.e['Minimap'].ui_size[1] + 10 + 27)
            upgrade_stack_size = math.floor(right_side_remaining_vertical / 13)
            for i, upgrade in enumerate(sorted([(self.owned_upgrades[upgrade], upgrade) for upgrade in self.owned_upgrades if self.owned_upgrades[upgrade]], reverse=True)):
                upgrade = upgrade[1]
                x_shift = i // upgrade_stack_size
                i = i % upgrade_stack_size
                upgrade_img = self.e['Assets'].images['upgrades'][upgrade + '_b']
                self.e['Renderer'].blit(upgrade_img, (self.e['Game'].display.get_width() - upgrade_img.get_width() - 4 + self.e['State'].right_inv_offset - x_shift * 22, self.e['Minimap'].ui_size[1] + 10 + i * 13), z=9997.1 - i * 0.0001, group='ui')
                amt_text = f'{self.owned_upgrades[upgrade]}x'
                if self.owned_upgrades[upgrade] > 1:
                    self.e['Text']['small_font'].renderzb_old(amt_text, (self.e['Game'].display.get_width() - self.e['Text']['small_font'].width(amt_text) - 14 + self.e['State'].right_inv_offset - x_shift * 22, self.e['Minimap'].ui_size[1] + 20 + i * 13), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998.5, group='ui')
        
            if self.e['Settings'].setting('show_fps') == 'enabled':
                fps_text = f'FPS: {int(self.e["Window"].fps)}'
                self.e['Text']['small_font'].renderzb(fps_text, (self.e['Game'].display.get_width() - self.e['Minimap'].ui_size[0] - 9 - self.e['Text']['small_font'].width(fps_text) + self.e['State'].right_inv_offset, 4), color=(254, 252, 211), bgcolor=(38, 27, 46), z=9998, group='ui')

        if not (self.e['Game'].player.dead or self.e['Transition'].progress or self.e['Transition'].level_end or self.ui_busy):
            notification_offset = 0
            for notification in self.notifications[::-1]:
                self.e['Text'][notification[3]].renderzb(notification[0], (self.e['Game'].display.get_width() / 2 - self.e['Text'][notification[3]].width(notification[0]) / 2, notification[1] - notification_offset), color=(254, 252, 211), bgcolor=(38, 27, 46), z=10001.5, group='ui')
                notification_offset += self.e['Text'][notification[3]].line_height + 6

            if not (self.e['Transition'].progress or self.e['Transition'].level_end or self.title or self.e['HUD'].hide_ui):
                active_effects = [effect for effect in self.effects if self.effects[effect][0]]

                # kinda hacked to include weapon abilities if enabled in settings
                primary_ability = WEAPON_STATS[self.e['Game'].player.weapon.type]['primary']
                secondary_ability = WEAPON_STATS[self.e['Game'].player.weapon.type]['secondary']
                ability_cooldowns = []
                if self.e['Settings'].player_cooldowns:
                    if self.e['Game'].player.weapon.shoot_cooldown[0]:
                        ability_cooldowns.append(primary_ability)
                    if self.e['Game'].player.weapon.secondary_cooldown[0]:
                        ability_cooldowns.append(secondary_ability)
                    if self.e['Game'].player.roll_cooldown:
                        ability_cooldowns.append('dodge')
                    if self.e['Game'].player.swap_cooldown:
                        ability_cooldowns.append('swap')
                
                for i, effect in enumerate(active_effects + ability_cooldowns):
                    if effect in ability_cooldowns:
                        # more hacks
                        if effect == primary_ability:
                            ratio = self.e['Game'].player.weapon.shoot_cooldown[0] / self.e['Game'].player.weapon.shoot_cooldown[1]
                        elif effect == 'swap':
                            ratio = self.e['Game'].player.swap_cooldown / self.e['Game'].player.swap_cooldown_amt
                        elif effect == 'dodge':
                            ratio = self.e['Game'].player.roll_cooldown / self.e['Game'].player.roll_cooldown_amt
                        elif effect == secondary_ability:
                            ratio = self.e['Game'].player.weapon.secondary_cooldown[0] / self.e['Game'].player.weapon.secondary_cooldown[1]
                        else:
                            continue
                    else:
                        dur = self.effects[effect][0]
                        ratio = 1 - dur / self.effects[effect][1]
                    offset_x = (i - (len(active_effects + ability_cooldowns) - 1) / 2) * 10
                    ratio = max(0, min(1, ratio))
                    img = self.e['Assets'].images['upgrades'][f'{effect}_b'].copy()
                    img_front = img.copy()
                    img.set_alpha(80)
                    if ratio < 1:
                        img_front.blit(pygame.Surface((img.get_width(), int((ratio * 0.75 + 0.125) * img.get_height()))), (0, 0))
                    img_front.set_colorkey((0, 0, 0))
                    self.e['Renderer'].blit(img, (self.e['Game'].player.center[0] - self.e['Game'].camera[0] - img.get_width() // 2 + offset_x, self.e['Game'].player.center[1] + 13 - self.e['Game'].camera[1] - img.get_height() // 2), z=9994, group='ui')
                    self.e['Renderer'].blit(img_front, (self.e['Game'].player.center[0] - self.e['Game'].camera[0] - img.get_width() // 2 + offset_x, self.e['Game'].player.center[1] + 13 - self.e['Game'].camera[1] - img.get_height() // 2), z=9995, group='ui')
                    self.e['Renderer'].blit(self.e['Assets'].images['upgrades']['frame'], (self.e['Game'].player.center[0] - self.e['Game'].camera[0] - img.get_width() // 2 + offset_x, self.e['Game'].player.center[1] + 13 - self.e['Game'].camera[1] - img.get_height() // 2), z=9996, group='ui')
    
        self.closest_entity = [None, 99999]
                
