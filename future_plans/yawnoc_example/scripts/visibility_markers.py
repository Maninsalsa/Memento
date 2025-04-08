import pygame

from . import pygpen as pp

class VisibilityMarkers(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

        self.markers = {}
        for marker in self.e['Assets'].images['machines']:
            if '_white' in marker:
                img = self.e['Assets'].images['machines'][marker]
                img.set_colorkey((0, 0, 0))
                self.markers[marker.replace('_white', '')] = pygame.mask.from_surface(img)

        self.reset()

    def insert(self, img, loc):
        mask = pygame.mask.from_surface(img)

        ts = self.e['Tilemap'].tile_size
        tl = (int(loc[0] // ts), int(loc[1] // ts))
        br = (int((loc[0] + img.get_width()) // ts), int((loc[1] + img.get_height()) // ts))
        for x in range(tl[0], br[0] + 1):
            for y in range(tl[1], br[1] + 1):
                if (x, y) not in self.mask_map:
                    self.mask_map[(x, y)] = []
                self.mask_map[(x, y)].append(((loc[0] - x * ts, loc[1] - y * ts), mask))

    def reset(self):
        self.mask_map = {}

    def render_marker(self, loc, marker_id, offset=(0, 0), color=(254, 252, 211)):
        if (loc in self.mask_map) and (marker_id in self.markers):
            marker = self.markers[marker_id]
            base_mask = pygame.mask.Mask(marker.get_size())
            for blocker in self.mask_map[loc]:
                base_mask.draw(blocker[1], (blocker[0][0] - offset[0], blocker[0][1] - offset[1]))
            base_mask = base_mask.overlap_mask(marker, offset=(0, 0))
            return base_mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
        else:
            return None
        
    def render_big_marker(self, loc, surf, color=(254, 252, 211)):
        ts = self.e['Tilemap'].tile_size
        gloc = (int(loc[0] // ts), int(loc[1] // ts))
        remainder = (loc[0] - gloc[0] * ts + surf.get_width(), loc[1] - gloc[1] * ts + surf.get_height())
        locs = [gloc]
        if remainder[0] >= ts:
            locs.append((gloc[0] + 1, gloc[1]))
        if remainder[1] >= ts:
            locs.append((gloc[0], gloc[1] + 1))
        if len(locs) == 3:
            locs.append((gloc[0] + 1, gloc[1] + 1))

        count = 0
        for bloc in locs:
            if bloc in self.mask_map:
                for blocker in self.mask_map[bloc]:
                    if not count:
                        src_mask = pygame.mask.from_surface(surf)
                        base_mask = pygame.mask.Mask(surf.get_size())

                    base_mask.draw(blocker[1], (blocker[0][0] + bloc[0] * ts - loc[0], blocker[0][1] + bloc[1] * ts - loc[1]))
                    count += 1

        if count:
            base_mask = base_mask.overlap_mask(src_mask, offset=(0, 0))
            return base_mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
        
        return None