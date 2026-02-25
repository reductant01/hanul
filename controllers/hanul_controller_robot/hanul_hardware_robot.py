"""
실제 로봇 하드웨어 인터페이스 (모터 ID 기반)
"""
import time
from common.omni_inverse_kinematics import OmniKinematics


class HanulHardware:
    """실제 한울 로봇: 모터/엔코더를 ID로 제어"""

    def __init__(self, motor_id_left=1, motor_id_right=2, motor_id_back=3, max_speed=6.0, control_hz=50.0):
        self.motor_id_left = motor_id_left
        self.motor_id_right = motor_id_right
        self.motor_id_back = motor_id_back
        self.control_hz = control_hz
        self.kinematics = OmniKinematics(max_speed=max_speed)
        self._vel_L = 0.0
        self._vel_R = 0.0
        self._vel_B = 0.0
        self._pos_L = 0.0
        self._pos_R = 0.0
        self._pos_B = 0.0
        self._lidar_connected = False

    def step(self):
        time.sleep(1.0 / self.control_hz)
        return 0

    def set_cmd_vel(self, vx, vy, w):
        target_L, target_R, target_B = self.kinematics.cmd_vel_to_motor_speed(vx, vy, w)
        self._vel_L, self._vel_R, self._vel_B = target_L, target_R, target_B
        self._send_motor_velocity(self._vel_L, self._vel_R, self._vel_B)

    def _send_motor_velocity(self, vel_L, vel_R, vel_B):
        pass

    def get_encoder_values(self):
        return (self._pos_L, self._pos_R, self._pos_B)

    def get_lidar_data(self):
        if not self._lidar_connected:
            return {"ranges": [], "fov": 0.0, "min_range": 0.0, "max_range": 0.0}
        return {"ranges": [], "fov": 0.0, "min_range": 0.0, "max_range": 0.0}

    def stop(self):
        self._send_motor_velocity(0.0, 0.0, 0.0)
