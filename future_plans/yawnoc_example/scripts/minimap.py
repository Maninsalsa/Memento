import pygame

from . import pygpen as pp

class Minimap(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.minimap = self.e['Machines'].minimap.copy()

        self.e['UIBoxer'].load('data/images/boxer')

    @property
    def ui_size(self):
        return (min(52 + self.e['State'].upgrade_stat('compass'), self.minimap.get_width()), min(53 + self.e['State'].upgrade_stat('compass'), self.minimap.get_height()))

    def update(self):
        self.minimap = self.e['Machines'].minimap.copy()
        player_pos = (int(self.e['Game'].player.pos[0] // self.e['Tilemap'].tile_size), int(self.e['Game'].player.pos[1] // self.e['Tilemap'].tile_size))
        self.minimap.set_at(player_pos, (131, 206, 62))
        self.frenemy_positions = []
        if 'frenemies' in self.e['EntityGroups'].groups:
            for frenemy in self.e['EntityGroups'].groups['frenemies']:
                frenemy_pos = (int(frenemy.pos[0] // self.e['Tilemap'].tile_size), int(frenemy.pos[1] // self.e['Tilemap'].tile_size))
                if frenemy.friendly:
                    self.minimap.set_at(frenemy_pos, (131, 206, 62))
                else:
                    self.minimap.set_at(frenemy_pos, (125, 43, 88))
                    self.frenemy_positions.append(frenemy_pos)

    def render(self):
        map_offset = [self.e['Game'].player.pos[0] / self.e['Tilemap'].tile_size - 26, self.e['Game'].player.pos[1] / self.e['Tilemap'].tile_size - 26]
        map_offset[0] = max(0, min(self.minimap.get_width() - self.ui_size[0], map_offset[0]))
        map_offset[1] = max(0, min(self.minimap.get_height() - self.ui_size[1], map_offset[1]))

        map_rect = pygame.Rect(*map_offset, self.ui_size[0], self.ui_size[1])

        map_subsurf = pp.utils.gfx.clip(self.minimap, map_rect).convert_alpha()
        map_subsurf.set_alpha(200)

        self.e['Renderer'].blit(map_subsurf, (self.e['Game'].display.get_width() - map_subsurf.get_width() - 4 + self.e['State'].right_inv_offset, 4), z=9997, group='ui')
        box_surf = self.e['UIBoxer'].ui_box('basic', (self.ui_size[0] + 6, self.ui_size[1] + 6)).copy()

        for cell in self.e['Machines'].important_cells.values():
            if not map_rect.collidepoint(cell.pos):
                mark_pos = (min(max(-1, cell.pos[0] - map_rect.left), map_rect.width), min(max(-1, cell.pos[1] - map_rect.top), map_rect.height))
                color = (125, 43, 88)
                if cell.type == 'chest':
                    color = (228, 103, 71)
                box_surf.set_at((mark_pos[0] + 3, mark_pos[1] + 3), color)
        
        for frenemy_pos in self.frenemy_positions:
            if not map_rect.collidepoint(frenemy_pos):
                mark_pos = (min(max(-1, frenemy_pos[0] - map_rect.left), map_rect.width), min(max(-1, frenemy_pos[1] - map_rect.top), map_rect.height))
                color = (125, 43, 88)
                box_surf.set_at((mark_pos[0] + 3, mark_pos[1] + 3), color)
        
        self.e['Renderer'].blit(box_surf, (self.e['Game'].display.get_width() - map_subsurf.get_width() - 7 + self.e['State'].right_inv_offset, 1), z=9998, group='ui')