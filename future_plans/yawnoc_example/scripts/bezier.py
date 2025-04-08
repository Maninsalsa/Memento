import math

import pygame

BEZIER_TYPES = {
    'bounce_out': [[2.4, 0.01], [1.25, 2.65]],
    'slow_in': [[0.91, 0.29], [0.98, -0.33]],
}

LINE_VFX = {
    'menu_item': {
        'points': [[0, 0], [90, 0], [102, -24]],
        'color': (254, 252, 211),
        'width': 1,
        'speed': 4,
        'time_cap': True,
        'scroll_affected': True,
        'poly_fill': False,
    },
    'menu_item_text_large': {
        'points': [[0, 0], [60, 0]],
        'color': (254, 252, 211),
        'width': 1,
        'speed': 4,
        'time_cap': True,
        'scroll_affected': True,
        'poly_fill': False,
    },
    'weapon_select_description': {
        'points': [[6, 6], [0, 0], [6, -6], [72, -6], [96, 18]],
        'color': (254, 252, 211),
        'width': 1,
        'speed': 4,
        'time_cap': True,
        'scroll_affected': True,
        'poly_fill': False,
    },
    'weapon_select_description_long': {
        'points': [[6, 6], [0, 0], [6, -6], [80, -6], [104, 18]],
        'color': (254, 252, 211),
        'width': 1,
        'speed': 4,
        'time_cap': True,
        'scroll_affected': True,
        'poly_fill': False,
    }
}

# https://www.desmos.com/calculator/ebdtbxgbq0
class CubicBezier():
    def __init__(self, *points):
        points = list(points)
        if len(points) not in [2, 4]:
            raise Exception('InvalidArgumentCountError')
        if len(points) == 2:
            points = [[0, 0]] + points + [[1, 1]]
        self.points = points

    def calculate(self, t):
        x = (1 - t) ** 3 * self.points[0][0] + 3 * t * (1 - t) ** 2 * self.points[1][0] + 3 * t ** 2 * (1 - t) * self.points[2][0] + t ** 3 * self.points[3][0]
        y = (1 - t) ** 3 * self.points[0][1] + 3 * t * (1 - t) ** 2 * self.points[1][1] + 3 * t ** 2 * (1 - t) * self.points[2][1] + t ** 3 * self.points[3][1]
        return [x,y]

    def calculate_x(self, t):
        return self.calculate(t)[0]

class LineChainVFX():
    def __init__(self, point_config, location, bezier, rate, color, width=1, time_cap=True, offset_affected=True, poly_fill=False):
        # point_config is [[x, y, t], ...]
        total_line_length = sum([math.sqrt((p[0] - point_config[i - 1][0]) ** 2 + (p[1] - point_config[i - 1][1]) ** 2) for i, p in enumerate(point_config) if i != 0])
        point_config_with_times = [point_config[0] + [0]]
        cumulative_length = 0
        self.point_config_raw = point_config
        for i, point in enumerate(point_config):
            if i != 0:
                cumulative_length += math.sqrt((point[0] - point_config[i - 1][0]) ** 2 + (point[1] - point_config[i - 1][1]) ** 2)
                point_config_with_times.append(point + [cumulative_length / total_line_length])
        self.point_config = point_config_with_times
        self.bezier = bezier
        self.time = 0
        self.rate = rate
        self.base_offset = location
        self.color = color
        self.width = width
        self.time_cap = time_cap
        self.offset_affected = offset_affected
        self.poly_fill = poly_fill

    def update(self, dt):
        if self.time_cap:
            self.time = max(min(self.time + self.rate * dt, 1), 0)
        else:
            self.time += self.rate * dt

    def draw(self, surf, offset=[0, 0], color=None):
        if not self.offset_affected:
            offset = [0, 0]

        offset = [-offset[0], -offset[1]]

        if not color:
            color = self.color

        if self.time > 0:
            length = self.bezier.calculate_x(self.time)
            for i, point in enumerate(self.point_config):
                if i != 0:
                    first_point = [self.point_config[i - 1][0] + self.base_offset[0] - offset[0], self.point_config[i - 1][1] + self.base_offset[1] - offset[1]]

                    if (point[2] < length) and (i != len(self.point_config) - 1):
                        pygame.draw.line(surf, color, first_point, [point[0] + self.base_offset[0] - offset[0], point[1] + self.base_offset[1] - offset[1]], self.width)

                    else:
                        dif_x = point[0] - self.point_config[i - 1][0]
                        dif_y = point[1] - self.point_config[i - 1][1]
                        relative_length = (length - self.point_config[i - 1][2]) / (point[2] - self.point_config[i - 1][2])
                        line_end = [self.point_config[i - 1][0] + dif_x * relative_length, self.point_config[i - 1][1] + dif_y * relative_length]
                        pygame.draw.line(surf, color, first_point, [line_end[0] + self.base_offset[0] - offset[0], line_end[1] + self.base_offset[1] - offset[1]], self.width)
                        break

        if (self.time >= 0.2) and self.poly_fill:
            point_set = [p[:2] for p in self.point_config]
            x_point_set = [p[0] for p in point_set]
            y_point_set = [p[1] for p in point_set]

            base_x = min(x_point_set)
            base_y = min(y_point_set)

            width = max(x_point_set) - base_x
            height = max(y_point_set) - base_y

            poly_surf = pygame.Surface((width + 1, height + 1))
            poly_surf.set_colorkey((0, 0, 0))
            poly_surf.set_alpha((self.time - 0.2) / 0.8 * 255)
            poly_render_set = [[p[0] - base_x, p[1] - base_y] for p in point_set]
            pygame.draw.polygon(poly_surf, self.color, poly_render_set)

            surf.blit(poly_surf, (base_x + self.base_offset[0] - offset[0], base_y + self.base_offset[1] - offset[1]))

def generate_line_chain_vfx(line_type, bezier_type, location):
    line_info = LINE_VFX[line_type]
    return LineChainVFX(line_info['points'], location, CubicBezier(*BEZIER_TYPES[bezier_type]), line_info['speed'], line_info['color'], line_info['width'], line_info['time_cap'], line_info['scroll_affected'], line_info['poly_fill'])