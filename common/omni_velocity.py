"""
옴니휠 cmd_vel → 모터 속도(가속 완화 포함) 공통 로직
"""
import math
from common.omni_inverse_kinematics import OmniKinematics

BOOST_THRESHOLD = 0.08
BOOST_SCALE = 15


class OmniVelocityController:

    def __init__(self, max_speed=6.0, acceleration_factor=0.1,
                 linear_speed_max=0.8, linear_speed_min=-0.8, linear_speed_min_vy=-0.8,
                 angular_speed_max=0.5, angular_speed_min=-0.5):
        self.kinematics = OmniKinematics(max_speed=max_speed)
        self.acceleration_factor = acceleration_factor
        self.linear_speed_max = linear_speed_max
        self.linear_speed_min = linear_speed_min
        self.linear_speed_min_vy = linear_speed_min_vy
        self.angular_speed_max = angular_speed_max
        self.angular_speed_min = angular_speed_min
        self.current_vel_L = 0.0
        self.current_vel_R = 0.0
        self.current_vel_B = 0.0

    def update(self, vx, vy, w):
        linear_mag = math.hypot(vx, vy)
        if 0.001 < linear_mag < BOOST_THRESHOLD:
            vx *= BOOST_SCALE
            vy *= BOOST_SCALE
        abs_w = abs(w)
        if 0.001 < abs_w < BOOST_THRESHOLD:
            w *= BOOST_SCALE
        vx = max(self.linear_speed_min, min(self.linear_speed_max, vx))
        vy = max(self.linear_speed_min_vy, min(self.linear_speed_max, vy))
        w = max(self.angular_speed_min, min(self.angular_speed_max, w))
        target_L, target_R, target_B = self.kinematics.cmd_vel_to_motor_speed(vx, vy, w)
        if abs(target_L) < 1e-6 and abs(target_R) < 1e-6 and abs(target_B) < 1e-6:
            self.current_vel_L = 0.0
            self.current_vel_R = 0.0
            self.current_vel_B = 0.0
            return (0.0, 0.0, 0.0)
        self.current_vel_L += self.acceleration_factor * (target_L - self.current_vel_L)
        self.current_vel_R += self.acceleration_factor * (target_R - self.current_vel_R)
        self.current_vel_B += self.acceleration_factor * (target_B - self.current_vel_B)
        return (self.current_vel_L, self.current_vel_R, self.current_vel_B)

    def reset(self):
        self.current_vel_L = 0.0
        self.current_vel_R = 0.0
        self.current_vel_B = 0.0
