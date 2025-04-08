import pygame

from . import pygpen as pp

PARTNERS = ['jim', 'oswald', 'hazel']

def generate_shadow_anims(game):
    for partner in PARTNERS:
        entity_data = game.e['EntityDB'].configs[partner]
        for anim in list(entity_data.animations):
            anim_copy = entity_data.animations[anim].hard_copy()
            anim_copy_2 = entity_data.animations[anim].hard_copy()
            entity_data.animations[f'{anim}_shadow'] = anim_copy
            entity_data.animations[f'{anim}_light'] = anim_copy_2
            entity_data.config['animations'][f'{anim}_shadow'] = entity_data.config['animations'][anim]
            entity_data.config['animations'][f'{anim}_light'] = entity_data.config['animations'][anim]
            for i, img in enumerate(anim_copy.images):
                anim_copy.images[i] = pygame.mask.from_surface(img).to_surface(setcolor=(38, 27, 46, 255), unsetcolor=(0, 0, 0, 0))
                anim_copy_2.images[i] = pygame.mask.from_surface(img).to_surface(setcolor=(254, 252, 211, 255), unsetcolor=(0, 0, 0, 0))

def prep_assets(assets):
    # the stump is the only machine with an alpha
    assets.images['machines']['stump'] = pygame.image.load('data/images/machines/stump.png').convert_alpha()

    assets.images['misc']['full_fade'] = pygame.transform.scale(pygame.image.load('data/images/misc/fade.png').convert_alpha(), (100, assets.e['Game'].display.get_height()))

    assets.images['misc']['shadow_small'].set_alpha(100)
    assets.images['misc']['shadow_medium'].set_alpha(100)
    assets.images['misc']['shadow_tiny'].set_alpha(100)

    BULLET_COLOR_LIST = ['red', 'blue', 'brown', 'purple']

    assets.bullets = {color: [] for color in BULLET_COLOR_LIST}
    for color in list(assets.bullets):
        assets.bullets[color + '_outlined'] = []
        assets.bullets[color + '_visibility'] = []

    bullet_core = assets.images['misc']['bullet_core']
    for i in range(360):
        rotated_core = pygame.transform.rotate(bullet_core, i)
        bullet_border_colors = [pygame.transform.rotate(assets.images['misc'][f'bullet_{color}'], i) for color in BULLET_COLOR_LIST]
        for img in bullet_border_colors:
            img.set_colorkey((0, 0, 0))
        rotated_core.set_colorkey((0, 0, 0))
        bullet_colors = [pygame.Surface((rotated_core.get_width() + 2, rotated_core.get_height() + 2)) for i in range(len(bullet_border_colors))]
        for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i, img in enumerate(bullet_colors):
                img.blit(bullet_border_colors[i], (1 + offset[0], 1 + offset[1]))

        for i, img in enumerate(bullet_colors):
            img.blit(rotated_core, (1, 1))
            img.set_colorkey((0, 0, 0))
            assets.bullets[BULLET_COLOR_LIST[i]].append(img)

            visibility_outline = pygame.Surface(img.get_size())
            visibility_outline.fill((254, 252, 211))
            visibility_outline.blit(img, (0, 0))
            visibility_outline.set_colorkey((254, 252, 211))
            assets.bullets[BULLET_COLOR_LIST[i] + '_visibility'].append(visibility_outline)

            outlined_img = pygame.Surface((img.get_width() + 2, img.get_height() + 2))
            pp.gfx_util.outline(outlined_img, img, (1, 1), (38, 27, 46))
            outlined_img.blit(img, (1, 1))
            outlined_img.set_colorkey((0, 0, 0))
            assets.bullets[BULLET_COLOR_LIST[i] + '_outlined'].append(outlined_img)

    for machine in list(assets.images['machines']):
        if '_white' not in machine:
            img = assets.images['machines'][machine]
            outlined_img = pygame.Surface((img.get_width() + 2, img.get_height() + 2))
            pp.gfx_util.outline(outlined_img, img, (1, 1), (38, 27, 46))
            outlined_img.set_colorkey((0, 0, 0))
            outlined_img.set_alpha(190)
            assets.images['machines'][machine + '_outlined'] = outlined_img
    
    for upgrade in list(assets.images['upgrades']):
        if upgrade.split('_')[-1] == 'b':
            src = assets.images['upgrades'][upgrade]
            fancy_upgrade = pygame.Surface((src.get_width() + 4, src.get_height() + 3))
            fancy_upgrade.set_colorkey((0, 0, 0))
            fancy_upgrade.blit(src, (2, 0))
            fancy_upgrade.blit(assets.images['misc']['upgrade_border'], (0, 0))
            assets.images['upgrades']['_'.join(upgrade.split('_')[:-1])] = fancy_upgrade
    
    for weapon in list(assets.images['weapons']):
        raw_img = assets.images['weapons'][weapon]
        mask = pygame.mask.from_surface(raw_img)
        bounding_rects = mask.get_bounding_rects()
        bounds = [9999, 0, 9999, 0]
        for rect in bounding_rects:
            bounds[0] = min(bounds[0], rect.left)
            bounds[1] = max(bounds[1], rect.right)
            bounds[2] = min(bounds[2], rect.top)
            bounds[3] = max(bounds[3], rect.bottom)
        bounding_rect = pygame.Rect(bounds[0], bounds[2], bounds[1] - bounds[0], bounds[3] - bounds[2])
        base_img = pp.gfx_util.clip(raw_img, bounding_rect)
        base_img.set_colorkey((0, 0, 0))
        white_outline = pygame.Surface((base_img.get_width() + 2, base_img.get_height() + 2))
        pp.gfx_util.outline(white_outline, base_img, (1, 1), (254, 252, 211))
        white_outline.blit(base_img, (1, 1))
        white_outline.set_colorkey((0, 0, 0))
        double_outline = pygame.Surface((white_outline.get_width() + 2, white_outline.get_height() + 2))
        pp.gfx_util.outline(double_outline, white_outline, (1, 1), (38, 27, 46))
        double_outline.blit(white_outline, (1, 1))
        double_outline.set_colorkey((0, 0, 0))
        flat_img = pygame.Surface(double_outline.get_size())
        flat_img.blit(pygame.mask.from_surface(base_img).to_surface(setcolor=(38, 27, 46), unsetcolor=(0, 0, 0, 255)), (2, 2))
        flat_img.set_colorkey((0, 0, 0))
        assets.images['weapons'][f'{weapon}_flat'] = flat_img
        assets.images['weapons'][f'{weapon}_icon'] = double_outline
        assets.images['weapons'][f'{weapon}_raw'] = base_img
