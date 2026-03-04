"""
3휠 옴니휠 오도메트리: 엔코더 값으로 위치·각도 계산
"""
import math


class OmniOdometry:
    """3휠 옴니휠 로봇 오도메트리"""

    def __init__(self, wheel_radius=0.05, wheelbase=0.1328, odom_scale_x=1.0, odom_scale_y=1.0):
        self.R = wheel_radius
        self.L = wheelbase
        self.odom_scale_x = odom_scale_x
        self.odom_scale_y = odom_scale_y
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_pos_L = 0.0
        self.last_pos_R = 0.0
        self.last_pos_B = 0.0
        self._first = True

    def update(self, pos_L, pos_R, pos_B):
        if self._first:
            self._first = False
            self.last_pos_L = pos_L
            self.last_pos_R = pos_R
            self.last_pos_B = pos_B
            return 0.0, 0.0, 0.0
        delta_L = (pos_L - self.last_pos_L) * self.R
        delta_R = (pos_R - self.last_pos_R) * self.R
        delta_B = (pos_B - self.last_pos_B) * self.R

        NOISE_THRESHOLD = 0.0001
        if abs(delta_L) < NOISE_THRESHOLD:
            delta_L = 0.0
        if abs(delta_R) < NOISE_THRESHOLD:
            delta_R = 0.0
        if abs(delta_B) < NOISE_THRESHOLD:
            delta_B = 0.0

        self.last_pos_L = pos_L
        self.last_pos_R = pos_R
        self.last_pos_B = pos_B

        delta_x = (delta_R - delta_L) / 1.73205
        raw_delta_y = (2.0 * delta_B - delta_L - delta_R) / 3.0
        delta_y = -raw_delta_y
        delta_theta = (delta_L + delta_R + delta_B) / (3.0 * self.L)

        avg_theta = self.theta + (delta_theta / 2.0)
        dx_world = delta_x * math.cos(avg_theta) - delta_y * math.sin(avg_theta)
        dy_world = delta_x * math.sin(avg_theta) + delta_y * math.cos(avg_theta)
        self.x += self.odom_scale_x * dx_world
        self.y += self.odom_scale_y * dy_world
        self.theta += delta_theta

        while self.theta > math.pi:
            self.theta -= 2.0 * math.pi
        while self.theta < -math.pi:
            self.theta += 2.0 * math.pi

        return delta_x, delta_y, delta_theta

    def get_pose(self):
        return self.x, self.y, self.theta

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_pos_L = 0.0
        self.last_pos_R = 0.0
        self.last_pos_B = 0.0
        self._first = True
