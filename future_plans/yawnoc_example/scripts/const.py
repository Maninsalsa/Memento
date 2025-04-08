import os

import pygame

from .util import nice_round

VERSION = '1.1.3'

DEMO = False

CWD = os.getcwd()

PRICE_SCALE = {
    'upgrade': 1.0,
    'enchant': 0.8,
    'weapon': 0.6,
}

ALT_SHOP_PREMIUM = 1.4

FRENEMY_LEVELS = {
    'jim': 10,
    'oswald': 20,
    'hazel': 30,
}

DEFAULT_SAVE = {
    'best_score': 0,
    'weapon_enchants': {},
    'tutorial_progress': 0,
    'tutorial_controller_progress': 0,
    'guide_progress': {
        'enchant_purchase': 0,
        'weapon_purchase': 0,
        'upgrade_purchase': 0,
        'daisy_talked': 0,
    },
    'catalog': {
        'weapons': [],
        'enchantments': [],
        'upgrades': [],
        'machines': [],
        'powerups': [],
        'automata': [],
    }
}

SETTINGS = {
    'fps_cap': {
        'name': 'FPS Cap',
        'options': ['30', '60', '90', '120', '144', '165', '240', 'uncapped'],
        'submenu': 'graphics',
    },
    'fullscreen': {
        'name': 'Fullscreen',
        'options': ['disabled', 'enabled'],
        'submenu': 'video',
    },
    'windowed_resolution': {
        'name': 'Windowed Resolution',
        'options': ['384x216', '768x432', '1152x648', '1536x864', '1920x1080', '2560x1440', '3840x2160', 'native'],
        'submenu': 'video',
    },
    'master_volume': {
        'name': 'Master Volume',
        'options': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
        'submenu': 'audio',
    },
    'sfx_volume': {
        'name': 'SFX Volume',
        'options': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
        'submenu': 'audio',
    },
    'music_volume': {
        'name': 'Music Volume',
        'options': ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
        'submenu': 'audio',
    },
    'aim_assist': {
        'name': 'Controller Aim Assist',
        'options': ['0%', '50%', '100%'],
        'submenu': 'accessibility',
    },
    'outline': {
        'name': 'Player Outline',
        'options': ['disabled', 'enabled'],
        'submenu': 'accessibility',
    },
    'machine_outline': {
        'name': 'Machine Outline',
        'options': ['disabled', 'enabled'],
        'submenu': 'accessibility',
    },
    'bullet_outline': {
        'name': 'Enemy Bullet Outline',
        'options': ['disabled', 'enabled'],
        'submenu': 'accessibility',
    },
    'show_fps': {
        'name': 'Show FPS',
        'options': ['disabled', 'enabled'],
        'submenu': 'graphics',
    },
    'swap_trigger_bumper': {
        'name': 'Swap Bumpers/Triggers',
        'options': ['disabled', 'enabled'],
        'submenu': 'controller input',
    },
    'pink_player': {
        'name': 'Pink Player',
        'options': ['disabled', 'enabled'],
        'submenu': 'accessibility',
    },
    'screenshake': {
        'name': 'Screenshake',
        'options': ['disabled', 'enabled'],
        'submenu': 'accessibility',
    },
    'saturation': {
        'name': 'Saturation',
        'options': ['70%', '80%', '90%', '95%', '100%'],
        'submenu': 'graphics',
    },
    'grass': {
        'name': 'Grass',
        'options': ['disabled', 'no breeze', 'enabled'],
        'submenu': 'graphics',
    },
    'trees': {
        'name': 'Trees',
        'options': ['no breeze', 'breezy'],
        'submenu': 'graphics',
    },
    'crt_effect': {
        'name': 'CRT Screen Effect',
        'options': ['0%', '25%', '50%', '75%', '100%'],
        'submenu': 'accessibility',
    },
    'camera_slack': {
        'name': 'Camera Slack',
        'options': ['disabled', 'enabled'],
        'submenu': 'accessibility',
    },
    'camera_mouse_influence': {
        'name': 'Camera Mouse Influence',
        'options': ['0%', '10%', '20%', '30%', '40%', '50%'],
        'submenu': 'accessibility',
    },
    'ability_cooldowns': {
        'name': 'Ability Cooldowns',
        'options': ['hud', 'player & hud'],
        'submenu': 'accessibility',
    },
    'back': {
        'name': 'Back',
        'options': [],
        'submenu': 'all',
    },
}

DIFFICULTY_OPTIONS = [0, 1, 2, 3]

OFFSET_N4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
OFFSET_N9 = [(x - 1, y - 1) for x in range(3) for y in range(3)]
OFFSET_N8 = [(x - 1, y - 1) for x in range(3) for y in range(3)]
OFFSET_N8.remove((0, 0))

STABLE_MACHINES = {'beacon', 'chest', 'stump', 'spawner'}

FRIENDLY_MACHINES = {'chest', 'stump'}

OBTAINABLE_POWERUPS = ['invincibility', 'collateral', 'lifesteal', 'freeze', 'double_barrel', 'extra_rounds', 'potion', 'potion', 'shield', 'flame', 'slow_motion', 'collector', 'thunderclap']

ABILITY_DURATIONS = {
    'invincibility': 5,
    'lifesteal': 12,
    'collateral': 12,
    'double_barrel': 15,
    'freeze': 7,
    'extra_rounds': 8,
    'potion': 0,
    'swiftness': 3,
    'deathspiral': 4,
    'cleanse': 4,
    'rampage': 16,
    'shield': 0,
    'flame': 15,
    'slow_motion': 5,
    'collector': 10,
    'thunderclap': 6.5,
    'storage': 100,
}

class TYPES:
    Machine = None
    CentipedeRig = None
    Frenemy = None
    Player = None
    Eye = None

DIFFICULTY_INFO = [
    {
        'name': 'Pest Control',
        'description': 'Damage Taken: -50%\nStep Interval: +50%\nStep Pause: +25%\nMachines: -25%\nBullet Speeds: -25%\nPotion Frequency: +50%\nEnchant Prices: +30%',
        'damage': 0.5,
        'enemy_health': 1.0,
        'step_interval': 1.5,
        'step_pause': 1.25,
        'machine_count': 0.75,
        'bullet_speed': 0.75,
        'enchant_price': 1.3,
    },
    {
        'name': 'Infestation',
        'description': 'Normal Difficulty',
        'damage': 1.0,
        'enemy_health': 1.0,
        'step_interval': 1.0,
        'step_pause': 1.0,
        'machine_count': 1.0,
        'bullet_speed': 1.0,
        'enchant_price': 1.0,
    },
    {
        'name': 'Invasion',
        'description': 'Step Interval: -20%\nMachines: +40%\nBullet Speed: +25%\nEnchant Prices: -15%',
        'damage': 1.0,
        'enemy_health': 1.0,
        'step_interval': 0.8,
        'step_pause': 1.0,
        'machine_count': 1.4,
        'bullet_speed': 1.25,
        'enchant_price': 0.85,
    },
    {
        'name': 'Apocalypse',
        'description': 'Step Interval: -30%\nMachines: +80%\nBullet Speed: +30%\nMachine Health: +50%\nEnchant Prices: -40%',
        'damage': 1.0,
        'enemy_health': 1.5,
        'step_interval': 0.7,
        'step_pause': 1.0,
        'machine_count': 1.8,
        'bullet_speed': 1.3,
        'enchant_price': 0.6,
    }
]

AUTOMATA_LOOKUP = {
    'summer': ('cgol', 'highlife'),
    'fall': ('brain', 'migraine'),
    'winter': ('blobell', 'blursed'),
    'void': ('lowdeath', 'lowdeath'),
}

AUTOMATA_INFO = {
    'cgol': {
        'name': 'Conway\'s Game of Life',
        'description': 'Machines spawn with 3 neighbors, persist with 2 or 3 neighbors, and die otherwise.\n\nConway\'s Game of life is the most well known non-trivial cellular automata. It was discovered by John Conway in 1970.',
    },
    'highlife': {
        'name': 'HighLife',
        'description': 'Machines spawn with 3, 5, or 6 neighbors, persist with 2 or 3 neighbors, and die otherwise.\n\nThis HighLife is a modified version of the Highlife ruleset created by Nathan Thompson in 1994, which does not spawn with 5 neighbors.',
    },
    'brain': {
        'name': 'Brian\'s Brain',
        'description': 'Machines spawn with 2 neighbors and die regardless of neighbor count. Machines take 3 steps to "die" and do not allow new machines in their place while dying.\n\nThe original Brian\'s Brain discovered by Brian Silverman in the 1990s kills cells in 2 steps instead of 3.',
    },
    'migraine': {
        'name': 'Brian\'s Migraine',
        'description': 'The ruleset functions the same as Brian\'s Brain, except the spawner machines that violate the rules will fire more frequently to create more machines.\n\nThe chaos gave Daisy a migraine.',
    },
    'blobell': {
        'name': 'B5/S3456',
        'description': 'Machines spawn with 5 neighbors, persist with 3, 4, 5, or 6 neighbors, and die otherwise.\n\nB5/S3456 (named Blobell by Daisy) is not a remarkable ruleset for any reason. It\'s incapable of leaving its bounding box and usually remains idle until interacted with.',
    },
    'blursed': {
        'name': 'B578/S34567',
        'description': 'Machines spawn with 3, 7, or 8 neighbors, persist with 3, 4, 5, 6, or 7 neighbors, and die otherwise.\n\nB578/S34567 (named Blursed by Daisy) is similar to B5/S3456. The notable difference is the increased allowable density of machines.',
    },
    'lowdeath': {
        'name': 'LowDeath',
        'description': 'Machines spawn with 3, 6, or 8 neighbors, persist with 2, 3, or 8 neighbors, and die otherwise.\n\nNamed in the 2010s after a Geometry Dash level named Low Death; a play on words referencing a level named High Life. The ruleset was discovered earlier, but refered to as B368/S238.',
    }
}

ALL_SHOP_UPGRADES = ['extra_rounds', 'heart', 'potion', 'scoped_weapons', 'swiftness', 'running_shoes', 'winged_bullets', 'stopwatch', 'frost_touch',
                 'ricochet', 'invincibility', 'fatstep', 'investing', 'revival', 'treasure_trove', 'thorns', 'close_call', 'sledgehammer',
                 'frequent_customer', 'flame', 'penetration', 'smokescreen', 'bullet_time', 'cleanse', 'shield', 'sludge', 'overstocked',
                 'meatshield', 'leftovers', 'chestplate', 'rolypoly', 'fast_hands', 'trigger_finger', 'gamblers_dice', 'all_natural',
                 'magnet', 'bug_spray', 'leg_day', 'magnifying_glass', 'mystery_item', 'swordsmans_pendant', 'shockwave', 'guards_buckle',
                 'hostile_environment', 'reinforced_steel', 'confusion', 'rampage', 'wizards_hat', 'charged_coffee', 'garys_charm', 'spiked_helmet',
                 'potato_farmer', 'cash_overflow', 'turret', 'hothead', 'compass', 'storage']

SHOP_UPGRADES = ALL_SHOP_UPGRADES.copy()
if DEMO:
    SHOP_UPGRADES = ['extra_rounds', 'heart', 'potion', 'scoped_weapons', 'swiftness', 'winged_bullets', 'stopwatch', 'frost_touch',
                 'ricochet', 'invincibility', 'fatstep', 'investing', 'revival', 'treasure_trove', 'thorns', 'sledgehammer',
                 'flame', 'bullet_time', 'cleanse', 'shield', 'sludge',
                 'all_natural',
                 'magnifying_glass', 'mystery_item', 'swordsmans_pendant', 'shockwave']
    
MACHINE_INFO = {
    'cube': {
        'name': 'Cube',
        'description': 'The Cube is the most common type of machine. It fires in the 4 cardinal directions.',
    },
    'cylinder': {
        'name': 'Barrel',
        'description': 'Barrels are dangerous at short range. They emit a powerful shockwave in all directions.',
    },
    'egg': {
        'name': 'Egg',
        'description': 'Eggs are delicate and mostly harmless until destroyed. They contain highly aggressive centipede mechs.',
    },
    'crab': {
        'name': 'Crab',
        'description': 'Crabs are strange machines that stand on 4 skinny legs and fire directly at any perceived threat.',
    },
    'bishop': {
        'name': 'Bishop',
        'description': 'Bishops are similar to Cubes and fire in 4 diagonal directions.',
    },
    'volcano': {
        'name': 'Volcano',
        'description': 'Volcanoes attack their targets at a distance by launching explosives that rain down from the sky. Keep moving!',
    },
    'sniper': {
        'name': 'Sniper',
        'description': 'The Sniper is a structurally weak machine that takes aim from long ranges and fires powerful bursts of projectiles.',
    },
    'neutral': {
        'name': 'Neutral',
        'description': 'Neutral machines are the most primitive form of the invading machines. They aren\'t inherently hostile.',
    },
    'spawner': {
        'name': 'Spawner',
        'description': 'The Spawner is a tough machine that doesn\'t directly fight, but they have a tendency to birth neighboring hostile machines.',
    },
    'beacon': {
        'name': 'Beacon',
        'description': 'The Beacon is the most powerful of the common machines. It\'s quite sturdy and changes between spiral and cardinal attacks.',
    },
    'bouncer': {
        'name': 'Bouncer',
        'description': 'Bouncers regularly launch projectiles in random directions that can bounce off of walls. They appear non-threatening until you get taken out from behind.',
    },
    'eye': {
        'name': 'World\'s Eye',
        'description': 'The apparent source of all of the machines. Not much is known about the eye.',
    },
}

UPGRADE_INFO = {
    'extra_rounds': {
        'name': 'Extra Rounds',
        'template': 'Increase weapon rate of fire by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.08,
        'base_price': 35,
        'frequency': 3,
    },
    'heart': {
        'name': 'Heart',
        'template': 'Increase max health by [STAT].',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 50,
        'frequency': 5,
    },
    'potion': {
        'name': 'Potion',
        'desc': 'Heals 2 + 20% missing health.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 25,
        'frequency': 12,
    },
    'overstocked': {
        'name': 'Overstocked',
        'desc': 'Gives a random weapon to your partner.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 120,
        'frequency': 1,
        'restrictions': {'partner': True, 'minimum_wave': 10},
    },
    'scoped_weapons': {
        'name': 'Scoped Weapons',
        'template': 'Increase weapon range by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.1,
        'base_price': 35,
        'frequency': 3,
    },
    'swiftness': {
        'name': 'Swiftness',
        'template': 'Increase movement speed by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.06,
        'base_price': 20,
        'frequency': 3.5,
    },
    'running_shoes': {
        'name': 'Running Shoes',
        'template': 'Increase movement speed by [STAT]% when your weapon primary is off cooldown.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.16,
        'base_price': 22,
        'frequency': 1.8,
    },
    'winged_bullets': {
        'name': 'Winged Bullets',
        'template': 'Increase bullet velocity by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.15,
        'base_price': 18,
        'frequency': 2,
    },
    'stopwatch': {
        'name': 'Stopwatch',
        'template': 'Reduce secondary cooldown by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.14,
        'base_price': 32,
        'frequency': 3,
    },
    'frost_touch': {
        'name': 'Frost Touch',
        'template': '[STAT]% chance to freeze machines on hit.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.06,
        'base_price': 40,
        'frequency': 2,
    },
    'ricochet': {
        'name': 'Ricochet',
        'template': 'Increase friendly bullet ricochet max by [STAT].',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 100,
        'frequency': 0.75,
    },
    'invincibility': {
        'name': 'Stardust',
        'template': 'Increase invincibility duration by [STAT]% after taking damage.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.125,
        'base_price': 90,
        'frequency': 1,
    },
    'fatstep': {
        'name': 'Fatstep',
        'template': 'Fire [STAT] projectile(s) when dodge rolling.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 15,
        'frequency': 1,
    },
    'investing': {
        'name': 'Investing',
        'template': 'Each chest drops [STAT] extra scrap.',
        'stat_pattern': 'linear',
        'stat_rate': 2,
        'base_price': 16,
        'frequency': 3,
    },
    'revival': {
        'name': 'Revival',
        'template': 'Revive with 50% health after taking fatal damage.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 180,
        'frequency': 0.5,
        'restrictions': {'minimum_wave': 10},
    },
    'treasure_trove': {
        'name': 'Treasure Trove',
        'template': 'Increases number of chests at the beginning of each wave by [STAT].',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 150,
        'frequency': 0.5,
        'restrictions': {'minimum_wave': 10},
    },
    'thorns': {
        'name': 'Thorns',
        'template': 'Fire [STAT] projectiles when taking damage.',
        'stat_pattern': 'linear',
        'stat_rate': 2,
        'base_price': 16,
        'frequency': 1,
    },
    'close_call': {
        'name': 'Close Call',
        'template': '[STAT]% chance to block damage taken below 25% health.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.09,
        'base_price': 67,
        'frequency': 1.5,
        'restrictions': {'minimum_wave': 10},
    },
    'sledgehammer': {
        'name': 'Sledgehammer',
        'template': 'Increases damage dealt to undamaged enemies by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.15,
        'base_price': 95,
        'frequency': 2.75,
        'restrictions': {'minimum_wave': 10},
    },
    'frequent_customer': {
        'name': 'Frequent Customer',
        'template': 'Increase shop frequency for owned upgrades by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.4,
        'base_price': 40,
        'frequency': 2,
        'restrictions': {'minimum_wave': 10},
    },
    'flame': {
        'name': 'Flame',
        'template': '[STAT]% chance to ignite machines on hit.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.09,
        'base_price': 17,
        'frequency': 3.5,
    },
    'penetration': {
        'name': 'Penetration',
        'template': '[STAT]% of excess damage is converted to penetration.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.4,
        'base_price': 150,
        'frequency': 1,
        'restrictions': {'minimum_wave': 10},
    },
    'smokescreen': {
        'name': 'Smokescreen',
        'template': 'Increase machine inaccuracy by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.16,
        'base_price': 14,
        'frequency': 1,
        'restrictions': {'minimum_wave': 20},
    },
    'bullet_time': {
        'name': 'Bullet Time',
        'template': 'Decrease enemy projectile speed by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.06,
        'base_price': 27,
        'frequency': 3,
        'restrictions': {'minimum_wave': 20},
    },
    'cleanse': {
        'name': 'Cleanse',
        'template': 'Secondary abilities destroy enemy projectiles within a radius of [STAT] (4s cooldown).',
        'stat_pattern': 'linear',
        'stat_rate': 42,
        'base_price': 39,
        'frequency': 2,
    },
    'sludge': {
        'name': 'Sludge',
        'template': '[STAT]% chance to turn a tile into anti-machine sludge after destruction.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.11,
        'base_price': 28,
        'frequency': 1.5,
    },
    'shield': {
        'name': 'Shielded',
        'template': '[STAT]% chance for chests to drop an extra shield.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.12,
        'base_price': 44,
        'frequency': 1.5,
    },
    'meatshield': {
        'name': 'Meatshield',
        'template': 'Increase partner hitbox radius by [STAT].',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 11,
        'frequency': 1,
        'restrictions': {'partner': True, 'minimum_wave': 10},
    },
    'leftovers': {
        'name': 'Leftovers',
        'template': 'Heals apply [STAT]% of their healing to partners.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.24,
        'base_price': 33,
        'frequency': 1,
        'restrictions': {'partner': True},
    },
    'chestplate': {
        'name': 'Chestplate',
        'template': 'Increase max partner health by [STAT].',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 24,
        'frequency': 2.5,
        'restrictions': {'partner': True},
    },
    'rolypoly': {
        'name': 'Roly-Poly',
        'template': 'Decrease dodge roll cooldown by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.11,
        'base_price': 47,
        'frequency': 1.5,
    },
    'fast_hands': {
        'name': 'Fast Hands',
        'template': 'Decrease weapon swap cooldown by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.18,
        'base_price': 26,
        'frequency': 1,
        'restrictions': {'minimum_wave': 10},
    },
    'trigger_finger': {
        'name': 'Trigger Finger',
        'template': 'Fire secondary ability when swapping to a weapon.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 16,
        'frequency': 1,
        'restrictions': {'owned': False, 'minimum_wave': 10},
    },
    'gamblers_dice': {
        'name': 'Gambler\'s Dice',
        'template': 'Induces an even chance to double chest rewards or catch miasma.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 16,
        'frequency': 0.5,
        'restrictions': {'owned': False, 'minimum_wave': 10},
    },
    'all_natural': {
        'name': 'All Natural',
        'template': 'Increase max health by 4 and prevent potions from appearing in the shop.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 16,
        'frequency': 0.5,
        'restrictions': {'owned': False},
    },
    'magnet': {
        'name': 'Magnet',
        'template': 'Increase drop pickup range by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.4,
        'base_price': 28,
        'frequency': 1,
    },
    'bug_spray': {
        'name': 'Bug Spray',
        'template': 'Decrease centipede spawn chance by [STAT]% upon egg destruction.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.28,
        'base_price': 31,
        'frequency': 1,
        'restrictions': {'minimum_wave': 10},
    },
    'leg_day': {
        'name': 'Leg Day',
        'template': 'Increase dodge roll force by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.1,
        'base_price': 19,
        'frequency': 1,
        'restrictions': {'minimum_wave': 10},
    },
    'magnifying_glass': {
        'name': 'Magnifying Glass',
        'template': 'Increase crit chance by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.16,
        'base_price': 50,
        'frequency': 4,
        'restrictions': {'minimum_wave': 10},
    },
    'mystery_item': {
        'name': 'Mystery Item',
        'template': 'Grants a random upgrade.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 22,
        'frequency': 2.5,
        'restrictions': {'minimum_wave': 10},
    },
    'swordsmans_pendant': {
        'name': 'Swordmaster\'s Pendant',
        'template': 'Reduces barrel shockwave radius by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.19,
        'base_price': 38,
        'frequency': 1.25,
    },
    'shockwave': {
        'name': 'Overheat',
        'template': 'Neighboring machines have a [STAT]% chance to ignite after destroying a machine.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.22,
        'base_price': 73,
        'frequency': 1.5,
    },
    'guards_buckle': {
        'name': 'Guard\'s Buckle',
        'template': 'Start every wave with 1 shield.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 200,
        'frequency': 0.5,
        'restrictions': {'owned': False, 'minimum_wave': 10},
    },
    'hostile_environment': {
        'name': 'Hostile Environment',
        'template': 'Sludge and fire deals [STAT]% more damage.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.25,
        'base_price': 65,
        'frequency': 1.5,
        'restrictions': {'minimum_wave': 20},
    },
    'reinforced_steel': {
        'name': 'Reinforced Steel',
        'template': 'Increase shield strength by [STAT]%.',
        'stat_pattern': 'exponential',
        'stat_rate': 0.2,
        'base_price': 46,
        'frequency': 0.75,
        'restrictions': {'minimum_wave': 10},
    },
    'confusion': {
        'name': 'Confusion',
        'template': '[STAT]% chance to confuse machines on hit.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.05,
        'base_price': 36,
        'frequency': 1.5,
        'restrictions': {'minimum_wave': 10},
    },
    'rampage': {
        'name': 'Rampage',
        'template': 'Refresh secondary cooldown after destroying 8 machines in 1 second (16s cooldown).',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 130,
        'frequency': 0.5,
        'restrictions': {'owned': False, 'minimum_wave': 20},
    },
    'wizards_hat': {
        'name': 'Wizard\'s Hat',
        'template': 'Reduce enchant prices by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.25,
        'base_price': 220,
        'frequency': 0.5,
        'restrictions': {'owned': False, 'minimum_wave': 20},
    },
    'charged_coffee': {
        'name': 'Charged Coffee',
        'template': 'Reduce effect cooldowns by [STAT]%.',
        'stat_pattern': 'inverse_exponential',
        'stat_rate': 0.12,
        'base_price': 36,
        'frequency': 1.0,
        'restrictions': {'minimum_wave': 20},
    },
    'garys_charm': {
        'name': 'Gary\'s Charm',
        'template': 'Dodge rolling grants a temporary shield (16s cooldown).',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 175,
        'frequency': 0.5,
        'restrictions': {'owned': False, 'minimum_wave': 10},
    },
    'spiked_helmet': {
        'name': 'Spiked Helmet',
        'template': 'Dodge rolls deal [STAT] more damage.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 24,
        'frequency': 1.0,
    },
    'potato_farmer': {
        'name': 'Potato Farmer',
        'template': 'Scrap drops sometimes include potatoes. Farming 23 potatoes grants a powerup.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 37,
        'frequency': 0.3,
        'restrictions': {'owned': False},
    },
    'cash_overflow': {
        'name': 'Cash Overflow',
        'template': 'Fire a projectile for each scrap collected.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 75,
        'frequency': 0.5,
        'restrictions': {'owned': False},
    },
    'turret': {
        'name': 'Turret',
        'template': 'Increase weapon fire rate by 50%, reduce speed while shooting by 50%.',
        'stat_pattern': 'linear',
        'stat_rate': 0.5,
        'base_price': 75,
        'frequency': 0.5,
        'restrictions': {'owned': False},
    },
    'hothead': {
        'name': 'Hothead',
        'template': 'Automatically ignite machines within [STAT] spaces.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 195,
        'frequency': 0.5,
        'restrictions': {'minimum_wave': 10},
    },
    'compass': {
        'name': 'Compass',
        'template': 'Increase minimap size by [STAT].',
        'stat_pattern': 'linear',
        'stat_rate': 3,
        'base_price': 29,
        'frequency': 2.25,
        'restrictions': {'minimum_wave': 10},
    },
    'storage': {
        'name': 'Storage',
        'template': 'All powerups are stored until the next attack.',
        'stat_pattern': 'linear',
        'stat_rate': 1,
        'base_price': 75,
        'frequency': 1.125,
        'restrictions': {'owned': False},
    },
    'next': {
        'name': 'Next Wave',
        'desc': '',
        'base_price': 0,
    }
}

UPGRADE_LIST = list(UPGRADE_INFO)
UPGRADE_LIST.remove('next')

if DEMO:
    UPGRADE_INFO['potion']['frequency'] = 12

def generate_description(upgrade_id, level):
    info = UPGRADE_INFO[upgrade_id]
    if 'desc' in info:
        return info['desc']
    
    stat_str = ''
    if info['stat_pattern'] == 'exponential':
        stat_str = nice_round(((1 + info['stat_rate']) ** level - 1) * 100)
    elif info['stat_pattern'] == 'inverse_exponential':
        stat_str = nice_round((1 - (1 - info['stat_rate']) ** level) * 100)
    else:
        # linear addition case
        stat_str = nice_round(info['stat_rate'] * level)
    return info['template'].replace('[STAT]', stat_str)

def raw_enchant_stat(enchant_type, enchant_level):
    enchant = ENCHANTS[enchant_type]
    
    if enchant['growth'] == 'exponential':
        return enchant['growth_factor'] ** enchant_level - 1
    if enchant['growth'] == 'inverse_exponential':
        return 1 - (1 - enchant['growth_factor']) ** enchant_level

ENCHANTS = {
    'vampirism': {
        'title': 'Vampiric',
        'name': 'Vampirism',
        'growth': 'exponential',
        'growth_factor': 1.0025,
        'text': '<stat>% chance to heal upon dealing damage.',
    },
    'precision': {
        'title': 'Precise',
        'name': 'Precision',
        'growth': 'exponential',
        'growth_factor': 1.035,
        'text': '<stat>% chance to critically strike.',
    },
    'overload': {
        'title': 'Overloaded',
        'name': 'Overload',
        'growth': 'exponential',
        'growth_factor': 1.025,
        'text': '<stat>% chance to double fire.',
    },
    'scrappy': {
        'title': 'Scavenging',
        'name': 'Scrappy',
        'growth': 'exponential',
        'growth_factor': 1.04,
        'text': '<stat>% chance to double scrap rewards.',
    },
    'hitrun': {
        'title': 'Bandit\'s',
        'name': 'Hit and Run',
        'growth': 'exponential',
        'growth_factor': 1.035,
        'text': '<stat>% chance to double movement speed upon destruction.',
    },
    'treasurehunter': {
        'title': 'Captain\'s',
        'name': 'Treasure Hunter',
        'growth': 'exponential',
        'growth_factor': 1.03,
        'text': '<stat>% chance to get a second drop from chests.',
    },
    'quickcharge': {
        'title': 'Charged',
        'name': 'Quickcharge',
        'growth': 'inverse_exponential',
        'growth_factor': 0.05,
        'text': 'Reduce secondary cooldown by <stat>%.',
    },
    'execution': {
        'title': 'Executioner\'s',
        'name': 'Execution',
        'growth': 'exponential',
        'growth_factor': 1.025,
        'text': '<stat>% chance to execute damaged non-boss machines.',
    },
    'sturdy': {
        'title': 'Sturdy',
        'name': 'Sturdy',
        'growth': 'inverse_exponential',
        'growth_factor': 0.026,
        'text': '<stat>% chance to block incoming damage.',
    },
    'heat': {
        'title': 'Flaming',
        'name': 'Heat',
        'growth': 'exponential',
        'growth_factor': 1.05,
        'text': '<stat>% chance to ignite machines on hit.',
    },
    'smite': {
        'title': 'Electrified',
        'name': 'Smite',
        'growth': 'exponential',
        'growth_factor': 1.007,
        'text': '<stat>% chance to smite for each excessive damage point dealt.',
    },
    'splash': {
        'title': 'Viral',
        'name': 'Splash',
        'growth': 'inverse_exponential',
        'growth_factor': 0.22,
        'text': '<stat>% chance to spread on-hit effects to neighboring machines.',
    },
    'fmj': {
        'title': 'Titanslayer',
        'name': 'Full Metal Jacket',
        'growth': 'exponential',
        'growth_factor': 1.09,
        'text': 'Deals <stat>% increased damage to bosses.',
    },
    'disarm': {
        'title': 'Peacekeeper\'s',
        'name': 'Disarm',
        'growth': 'inverse_exponential',
        'growth_factor': 0.06,
        'text': '<stat>% chance to disarm machines on hit.',
    },
    'cracked': {
        'title': 'Cracked',
        'name': 'Cracked',
        'growth': 'exponential',
        'growth_factor': 1.05,
        'text': 'Deals <stat>% increased damage to damaged enemies.',
    },
    'buggy': {
        'title': 'Infested',
        'name': 'Buggy',
        'growth': 'inverse_exponential',
        'growth_factor': 0.06,
        'text': '<stat>% chance to spawn a friendly centipede upon killing a machine.',
    },
    'cheer': {
        'title': 'Cheerful',
        'name': 'Cheer',
        'growth': 'exponential',
        'growth_factor': 1.028,
        'text': 'Increase rate of fire of other weapons by <stat>%.'
    },
}

WEAPON_STATS = {
    'rifle': {
        'name': 'Rifle',
        'desc': 'A standard rifle. It\'s a well rounded weapon.',
        'base_price': 100,
        'firerate': 8,
        'range': 0.4,
        'inaccuracy': 0.135,
        'damage': 1,
        'shots': 1,
        'advance': 20,
        'speed': 370,
        'primary': 'shoot',
        'secondary': 'piercing_round',
        'secondary_cooldown': 6,
        'shot_sound': 'shoot',
        'animated': False,
    },
    'pistol': {
        'name': 'Pistol',
        'desc': 'A small sidearm that comes with a grenade.',
        'base_price': 100,
        'firerate': 4.5,
        'range': 0.55,
        'damage': 1.5,
        'inaccuracy': 0.07,
        'shots': 1,
        'advance': 9,
        'speed': 320,
        'primary': 'shoot',
        'secondary': 'grenade',
        'secondary_cooldown': 10,
        'shot_sound': 'pistol_shoot',
        'animated': False,
    },
    'shotgun': {
        'name': 'Shotgun',
        'desc': 'A shotgun. Inaccurate, but powerful at close range.',
        'base_price': 100,
        'firerate': 1.8,
        'range': 0.2,
        'inaccuracy': 0.5,
        'damage': 1,
        'shots': 7,
        'advance': 19,
        'speed': 250,
        'primary': 'shoot',
        'secondary': 'birdshot',
        'secondary_cooldown': 8,
        'shot_sound': 'shotgun_shoot',
        'animated': False,
    },
    'quaker': {
        'name': 'Quaker',
        'desc': 'A bulky weapon that can raise up earth.',
        'base_price': 80,
        'firerate': 1.3,
        'range': 0.3,
        'inaccuracy': 0.2,
        'damage': 13,
        'shots': 1,
        'advance': 17,
        'speed': 150,
        'primary': 'shoot',
        'secondary': 'quake',
        'secondary_cooldown': 2.5,
        'shot_sound': 'heavy_fire',
        'animated': False,
    },
    'warpgun': {
        'name': 'Warpgun',
        'desc': 'A strangely shaped weapon capable of warping space.',
        'base_price': 50,
        'firerate': 0.7,
        'range': 0.5,
        'inaccuracy': 0.1,
        'damage': 3,
        'shots': 1,
        'advance': 12,
        'speed': 450,
        'primary': 'warp_mark',
        'secondary': 'warp',
        'secondary_cooldown': 0.5,
        'shot_sound': 'pistol_shoot',
        'animated': False,
    },
    'bow': {
        'name': 'Bow',
        'desc': 'A bow crafted out of local flora.',
        'base_price': 140,
        'firerate': 2,
        'range': 1.0,
        'inaccuracy': 0.04,
        'damage': 3,
        'penetration': 1,
        'shots': 1,
        'advance': 7,
        'speed': 350,
        'primary': 'arrow_shoot',
        'secondary': 'arrow_barrage',
        'secondary_cooldown': 6,
        'shot_sound': 'arrow_fire',
        'animated': True,
    },
    'beamer': {
        'name': 'Beamer',
        'desc': 'A strong rifle with an extremely high rate of fire.',
        'base_price': 200,
        'firerate': 18,
        'range': 0.375,
        'inaccuracy': 0.135,
        'damage': 0.5,
        'shots': 1,
        'advance': 20,
        'speed': 370,
        'primary': 'shoot',
        'secondary': 'extra_rounds',
        'secondary_cooldown': 28,
        'shot_sound': 'light_shoot',
        'animated': False,
        'minimum_wave': 10,
    },
    'revolver': {
        'name': 'Revolver',
        'desc': 'A powerful weapon, but a pain to reload.',
        'base_price': 100,
        'firerate': 6,
        'range': 0.35,
        'inaccuracy': 0.16,
        'damage': 5,
        'shots': 1,
        'advance': 9,
        'speed': 320,
        'primary': 'shoot',
        'secondary': 'quickdraw',
        'secondary_cooldown': 9,
        'shot_sound': 'pistol_shoot',
        'animated': False,
    },
    'predator': {
        'name': 'Predator',
        'desc': 'A powerful sniper rifle with high mobility.',
        'base_price': 100,
        'firerate': 1,
        'range': 1.2,
        'inaccuracy': 0.0,
        'damage': 6,
        'penetration': 3,
        'shots': 1,
        'advance': 25,
        'speed': 420,
        'primary': 'shoot',
        'secondary': 'backstep',
        'secondary_cooldown': 4,
        'shot_sound': 'sniper_shoot',
        'animated': False,
    },
    'wintersbreath': {
        'name': 'Winter\'s Breath',
        'desc': 'A compact weapon that brings the force of winter to the forest.',
        'base_price': 130,
        'firerate': 7,
        'range': 0.165,
        'inaccuracy': 0.9,
        'damage': 1,
        'shots': 3,
        'advance': 9,
        'speed': 150,
        'primary': 'shoot',
        'secondary': 'freeze',
        'secondary_cooldown': 28,
        'shot_sound': 'light_shoot',
        'animated': False,
    },
    'chaosring': {
        'name': 'Chaos Ring',
        'desc': 'A strange rounded weapon bringing chaos to battle with the ability warp space.',
        'base_price': 130,
        'firerate': 1,
        'range': 0.2,
        'inaccuracy': 0.25,
        'damage': 1.5,
        'penetration': 50,
        'shots': 16,
        'speed': 370,
        'advance': 7,
        'primary': 'warpshot',
        'secondary': 'deathspiral',
        'secondary_cooldown': 16,
        'shot_sound': 'cleanse',
        'animated': False,
        'minimum_wave': 10,
    },
    'neutralizer': {
        'name': 'Neutralizer',
        'desc': 'A rifle designed for neutralizing machine hostility.',
        'base_price': 150,
        'firerate': 11,
        'range': 0.37,
        'inaccuracy': 0.135,
        'damage': 1,
        'shots': 1,
        'advance': 15,
        'speed': 370,
        'primary': 'shoot',
        'secondary': 'neutralize',
        'secondary_cooldown': 7,
        'shot_sound': 'shoot',
        'animated': False,
    },
    'supernova': {
        'name': 'Supernova',
        'desc': 'A powerful shotgun capable of quickly clearing clusters of enemies.',
        'base_price': 220,
        'firerate': 2.6,
        'range': 0.2,
        'inaccuracy': 0.5,
        'damage': 1,
        'shots': 8,
        'advance': 19,
        'speed': 250,
        'primary': 'shoot',
        'secondary': 'collateral',
        'secondary_cooldown': 12,
        'shot_sound': 'shotgun_shoot',
        'animated': False,
        'minimum_wave': 10,
    },
    'moneygun': {
        'name': 'Moneygun',
        'desc': 'A weapon truly for the rich. Shooting it consumes scrap.',
        'base_price': 150,
        'firerate': 10,
        'range': 0.35,
        'inaccuracy': 0.15,
        'damage': 3.5,
        'shots': 1,
        'penetration': 1,
        'advance': 15,
        'speed': 340,
        'primary': 'shoot',
        'secondary': 'scrap_bomb',
        'secondary_cooldown': 8,
        'shot_sound': 'shoot',
        'animated': False,
        'minimum_wave': 10,
    },
    'handcanon': {
        'name': 'Handcanon',
        'desc': 'A high caliber sniper capable of dealing heavy damage.',
        'base_price': 125,
        'firerate': 0.7,
        'range': 1.2,
        'inaccuracy': 0.0,
        'damage': 15,
        'penetration': 1,
        'shots': 1,
        'advance': 25,
        'speed': 420,
        'primary': 'shoot',
        'secondary': 'phase_round',
        'secondary_cooldown': 7,
        'shot_sound': 'sniper_shoot',
        'animated': False,
        'minimum_wave': 10,
    },
    'carnelianblade': {
        'name': 'Carnelian Blade',
        'desc': 'A red colored blade believed to be a relic of the past.',
        'base_price': 100,
        'firerate': 1.5,
        'range': 1,
        'inaccuracy': 0.0,
        'damage': 2.2,
        'penetration': 999,
        'shots': 1,
        'advance': 0,
        'speed': 0,
        'primary': 'spin_slash',
        'secondary': 'dash_slash',
        'secondary_cooldown': 4,
        'shot_sound': 'spin',
        'animated': False,
        'minimum_wave': 10,
    },
    'dagger': {
        'name': 'Dagger',
        'desc': 'A plain dagger. Who knows what it could have been used for...',
        'base_price': 65,
        'firerate': 2.2,
        'range': 1,
        'inaccuracy': 0.0,
        'damage': 3.6,
        'penetration': 999,
        'shots': 1,
        'advance': 0,
        'speed': 0,
        'primary': 'spin_slash',
        'secondary': 'guard',
        'secondary_cooldown': 6.5,
        'shot_sound': 'spin',
        'animated': False,
    },
    'dragonsbreath': {
        'name': 'Dragon\'s Breath',
        'desc': 'A standard rifle. It\'s a well rounded weapon.',
        'base_price': 100,
        'firerate': 26,
        'range': 0.4,
        'inaccuracy': 0.85,
        'damage': 0.15,
        'penetration': 2,
        'shots': 1,
        'advance': 21,
        'speed': 180,
        'primary': 'shoot',
        'secondary': 'calamity',
        'secondary_cooldown': 8,
        'shot_sound': 'light_shoot',
        'animated': False,
        'minimum_wave': 16,
    },
    'bazooka': {
        'name': 'Bazooka',
        'desc': 'A powerful rocket launcher capable of dealing damage to large areas.',
        'base_price': 100,
        'firerate': 0.25,
        'range': 0.55,
        'inaccuracy': 0.05,
        'damage': 1,
        'shots': 1,
        'advance': 11,
        'speed': 200,
        'primary': 'rocket_launch',
        'secondary': 'nuke',
        'secondary_cooldown': 32,
        'shot_sound': 'arrow_fire',
        'animated': False,
        'minimum_wave': 16,
    },
    'jokers_gun': {
        'name': 'Joker\'s Gun',
        'desc': 'A twisted weapon that warps the nature of projectiles.',
        'base_price': 100,
        'firerate': 6,
        'range': 0.3,
        'inaccuracy': 0.135,
        'damage': 1.6,
        'shots': 1,
        'advance': 20,
        'speed': 370,
        'primary': 'goofy_shot',
        'secondary': 'jokers_guise',
        'secondary_cooldown': 15,
        'shot_sound': 'shoot',
        'animated': False,
        'minimum_wave': 16,
    },
    'ember': {
        'name': 'Ember',
        'desc': 'A bow capable of shooting flaming arrows.',
        'base_price': 140,
        'firerate': 4.25,
        'range': 0.6,
        'inaccuracy': 0.04,
        'damage': 2.5,
        'penetration': 1,
        'shots': 1,
        'advance': 7,
        'speed': 350,
        'primary': 'flaming_arrow',
        'secondary': 'firebomb',
        'secondary_cooldown': 5,
        'shot_sound': 'arrow_fire',
        'animated': True,
        'minimum_wave': 10,
    },
    'mire': {
        'name': 'Mire',
        'desc': 'A weapon forged of mud and vines capable of turning ground to sludge.',
        'base_price': 120,
        'firerate': 1.4,
        'range': 0.185,
        'inaccuracy': 0.6,
        'damage': 1.2,
        'shots': 12,
        'advance': 19,
        'speed': 250,
        'primary': 'shoot',
        'secondary': 'sludgebomb',
        'secondary_cooldown': 9.5,
        'shot_sound': 'shotgun_shoot',
        'animated': False,
    },
}

WEAPON_ABILITY_INFO = {
    'shoot': {
        'name': 'Shoot',
        'description': 'Fire the weapon normally.',
    },
    'warp_mark': {
        'name': 'Warp Mark',
        'description': 'Fire a projectile that marks a location for warping.',
    },
    'arrow_shoot': {
        'name': 'Arrow',
        'description': 'Fire an arrow. The bow must be drawn first.',
    },
    'flaming_arrow': {
        'name': 'Flaming Arrow',
        'description': 'Fire a flaming arrow. The bow must be drawn first.',
    },
    'piercing_round': {
        'name': 'Piercing Round',
        'description': 'Fire a powerful round that pierces through targets.',
    },
    'grenade': {
        'name': 'Grenade',
        'description': 'Throw a grenade that explodes on impact.',
    },
    'birdshot': {
        'name': 'Birdshot',
        'description': 'Fire a birdshot round resulting in 4x the normal amount of projectiles.',
    },
    'sludgebomb': {
        'name': 'Sludgebomb',
        'description': 'Fire an explosive round that thrashes the land and converts it into sludge.'
    },
    'quake': {
        'name': 'Quake',
        'description': 'Fire a quake round that raises up earth to create a barrier.',
    },
    'warp': {
        'name': 'Warp',
        'description': 'Warp to a marked location if a mark is available.',
    },
    'arrow_barrage': {
        'name': 'Arrow Barrage',
        'description': 'Fire a barrage of 11 arrows. The bow must be drawn first.',
    },
    'firebomb': {
        'name': 'Firebomb',
        'description': 'Fire an arrow that explodes with flame. The bow must be drawn first.',
    },
    'quickdraw': {
        'name': 'Quickdraw',
        'description': 'Reset all primary weapon cooldowns.',
    },
    'backstep': {
        'name': 'Backstep',
        'description': 'Dodge roll backwards to stay out of danger.'
    },
    'freeze': {
        'name': 'Freeze',
        'description': 'Temporarily freeze all machines. This doesn\'t count as a local status effect.',
    },
    'deathspiral': {
        'name': 'Death Spiral',
        'description': 'Passively fire out a double spiral of friendly projectiles.'
    },
    'neutralize': {
        'name': 'Neutralize',
        'description': 'Fire a burst of projectiles that neutralize all machines hit.',
    },
    'collateral': {
        'name': 'Collateral Damage',
        'description': 'Provides the Collateral Damage effect that causes destroyed machines to fire friendly projectiles.',
    },
    'scrap_bomb': {
        'name': 'Scrap Bomb',
        'description': 'Remotely detonates all scrap on the ground.',
    },
    'phase_round': {
        'name': 'Phase Round',
        'description': 'Fire a wide projectile capable of moderate penetration.',
    },
    'dash_slash': {
        'name': 'Dash Slash',
        'description': 'Dash quickly in a direction while dealing heavy damage to targets in the path.',
    },
    'guard': {
        'name': 'Guard',
        'description': 'Enter a defensive stance that briefly provides a small shield.',
    },
    'spin_slash': {
        'name': 'Spin Slash',
        'description': 'Quickly swing the weapon around in a circle.',
    },
    'calamity': {
        'name': 'Calamity',
        'description': 'Smite all machines locally affected by a negative status effect.',
    },
    'extra_rounds': {
        'name': 'Extra Rounds',
        'description': 'Provides the Extra Rounds effect that increases weapon firerate by 65%.',
    },
    'warpshot': {
        'name': 'Warpshot',
        'description': 'Fire several piercing projectiles that induce teleportation when they collide with terrain.',
    },
    'rocket_launch': {
        'name': 'Rocket Launch',
        'description': 'Fire an explosive rocket that deals damage to a wide area upon impact.',
    },
    'nuke': {
        'name': 'Nuke',
        'description': 'Drops an extremely powerful bomb at a target location.',
    },
    'goofy_shot': {
        'name': 'Goofy Shot',
        'description': 'Fire a projectile that cauzes a hazardous explosion of enemy projectiles upon machine destruction.',
    },
    'jokers_guise': {
        'name': 'Joker\'s Guise',
        'description': 'Invert all blue and red projectile types.',
    },
}

WEAPON_NAMES = {weapon: WEAPON_STATS[weapon]['name'] for weapon in WEAPON_STATS}

class Difficulties:
    EASY = 0
    NORMAL = 1
    HARD = 2
    EXTRAHARD = 3

    @staticmethod
    def info(difficulty):
        return DIFFICULTY_INFO[difficulty]

KEYBOARD_ICONS = {
    pygame.K_LCTRL: 'lctrl',
    pygame.K_RCTRL: 'rctrl',
    pygame.K_LSHIFT: 'lshift',
    pygame.K_RSHIFT: 'rshift',
    pygame.K_SPACE: 'space',
    pygame.K_TAB: 'tab',
    pygame.K_UP: 'up',
    pygame.K_DOWN: 'down',
    pygame.K_RIGHT: 'right',
    pygame.K_LEFT: 'left',
    pygame.K_ESCAPE: 'esc',
}

for binding in KEYBOARD_ICONS:
    KEYBOARD_ICONS[binding] = (KEYBOARD_ICONS[binding], (0, 0))

for i, char in enumerate('abcdefghijklmnopqrstuvwxyz'):
    KEYBOARD_ICONS[ord(char)] = ('general', (i, 0))

for i, char in enumerate('0123456789'):
    KEYBOARD_ICONS[ord(char)] = ('general', (i, 1))