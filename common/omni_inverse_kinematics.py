"""
3휠 옴니휠 역기구학 (vx, vy, w) → (motor_left, motor_right, motor_back)
"""


class OmniKinematics:
    """3휠 옴니휠 로봇 역기구학"""

    def __init__(self, max_speed=7.0):
        self.MAX_SPEED = max_speed

    def cmd_vel_to_motor_speed(self, vx, vy, w):
        motor_left = (-0.5 * vy - 0.866 * vx + w) * self.MAX_SPEED
        motor_right = (-0.5 * vy + 0.866 * vx + w) * self.MAX_SPEED
        motor_back = (1.0 * vy + w) * self.MAX_SPEED

        return self.clamp_speed(motor_left, motor_right, motor_back)

    def clamp_speed(self, motor_left, motor_right, motor_back):
        max_vel = max(abs(motor_left), abs(motor_right), abs(motor_back))
        if max_vel > self.MAX_SPEED:
            scale = self.MAX_SPEED / max_vel
            motor_left *= scale
            motor_right *= scale
            motor_back *= scale

        return motor_left, motor_right, motor_back
