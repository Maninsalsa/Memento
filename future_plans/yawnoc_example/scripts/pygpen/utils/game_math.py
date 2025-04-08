import math

import pygame

SQRT2 = math.sqrt(2)

def normalize(v, amt, target=0):
    if v > target + amt:
        v -= amt
    elif v < target - amt:
        v += amt
    else:
        v = target
    return v

def rectify(p1, p2):
    tl = (min(p1[0], p2[0]), min(p1[1], p2[1]))
    br = (max(p1[0], p2[0]), max(p1[1], p2[1]))
    return pygame.Rect(*tl, br[0] - tl[0] + 1, br[1] - tl[1] + 1)

def box_points(rect):
    points = []
    for y in range(rect.height):
        for x in range(rect.width):
            points.append((rect.x + x, rect.y + y))
    return points

def advance(vec, angle, amt):
    vec[0] += math.cos(angle) * amt
    vec[1] += math.sin(angle) * amt
    return vec

def fast_range_check(p1, p2, dis):
    grid_dis = abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])
    if grid_dis <= SQRT2 * dis:
        return distance(p1, p2) <= dis
    return False

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

# similar to normalize(), but used for rotations in radians
def rotate_towards(angle, target, amt):
    offset = (target - angle) % (math.pi * 2)
    if offset > math.pi:
        offset -= math.pi * 2
    if abs(offset) > amt:
        if offset > 0:
            return angle + amt
        if offset < 0:
            return angle - amt
    else:
        return target
    
# modified Bresenham
def grid_line(start, end):
    points = [tuple(start)]
    
    start = list(start)
    end = list(end)
    dx = abs(end[0] - start[0])
    dy = -abs(end[1] - start[1])
    xstep = 1 if start[0] < end[0] else -1
    ystep = 1 if start[1] < end[1] else -1
    error = dx + dy
    
    while (start[0] != end[0]) or (start[1] != end[1]):
        if 2 * error - dy > dx - 2 * error:
            error += dy
            start[0] += xstep
        else:
            error += dx
            start[1] += ystep
        
        points.append(tuple(start))
    
    return points
