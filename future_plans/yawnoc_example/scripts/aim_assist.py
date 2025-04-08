import math

from . import pygpen as pp

PULL_RANGE = 0.4

class AimAssist(pp.ElementSingleton):
    def __init__(self):
        super().__init__()

    @property
    def pull_range(self):
        return PULL_RANGE * self.e['Settings'].aim_assist

    def calc_pull(self, target_angle):
        angle = target_angle - (math.pi * 2) if target_angle > math.pi else target_angle
        return min(1.7, max(2 - abs(angle) / self.pull_range, 0)) * self.pull_range
    
    def apply_pulls(self, aim_angle, angle_1, angle_2, pull_1=0, pull_2=0):
        # only calculate a net pull if the pulling is in opposite directions
        if (angle_1 < math.pi) and (angle_2 > math.pi):
            net_pull = pull_1 - pull_2
            if net_pull >= 0:
                return self.apply_pull(aim_angle, angle_1, net_pull)
            else:
                return self.apply_pull(aim_angle, angle_2, -net_pull)
        elif pull_1 > pull_2:
            return self.apply_pull(aim_angle, angle_1, pull_1)
        else:
            return self.apply_pull(aim_angle, angle_2, pull_2)

    
    def apply_pull(self, aim_angle, target_angle, pull):
        if target_angle < math.pi:
            aim_angle += min(pull, target_angle)
        else:
            aim_angle += max(-pull, target_angle - math.pi * 2)
        return aim_angle

    def apply(self, aim_offset):
        angle = math.atan2(aim_offset[1], aim_offset[0])
        dis = pp.game_math.distance(aim_offset, (0, 0))

        adjusted_angle = angle

        relative_angles = [((m[0] - angle) % (math.pi * 2), m[1], m[2]) for m in self.e['Machines'].machines_in_range]
        relative_angles.sort()
        if len(relative_angles):
            if len(relative_angles) > 1:
                pull_1 = self.calc_pull(relative_angles[0][0])
                pull_2 = self.calc_pull(relative_angles[-1][0])
                adjusted_angle = self.apply_pulls(angle, relative_angles[0][0], relative_angles[-1][0], pull_1, pull_2)
            else:
                pull = self.calc_pull(relative_angles[0][0])
                adjusted_angle = self.apply_pulls(angle, relative_angles[0][0], 0, pull, 0)
        
        if adjusted_angle != angle:
            aim_offset = [math.cos(adjusted_angle) * dis, math.sin(adjusted_angle) * dis]
        return aim_offset
