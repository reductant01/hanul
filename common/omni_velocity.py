"""
옴니휠 cmd_vel → 모터 속도(가속 완화 포함) 공통 로직
"""
from common.omni_inverse_kinematics import OmniKinematics


class OmniVelocityController:
    """cmd_vel (vx, vy, w)를 역기구학 + 가속 완화하여 (vel_L, vel_R, vel_B)로 변환"""

    def __init__(self, max_speed=6.0, acceleration_factor=0.1):
        self.kinematics = OmniKinematics(max_speed=max_speed)
        self.acceleration_factor = acceleration_factor
        self.current_vel_L = 0.0
        self.current_vel_R = 0.0
        self.current_vel_B = 0.0

    def update(self, vx, vy, w):
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
