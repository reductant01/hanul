"""
NUC 실제 로봇 하드웨어 인터페이스 (다이나믹셀 ID 1=오른쪽, 2=뒤, 3=왼쪽)
Dynamixel Wizard 기준: ttyUSB1, 1000000 bps, Protocol 2.0, Operating Mode = Velocity(1),
Velocity Limit = 330 (75.57 rev/min), ID 1/2/3 = 오른쪽/뒤/왼쪽
"""
import math
import os
import time
from common.omni_velocity import OmniVelocityController

try:
    from dynamixel_sdk import PortHandler, PacketHandler  # type: ignore[reportMissingImports]
    _DXL_AVAILABLE = True
except ImportError:
    _DXL_AVAILABLE = False

PROTOCOL_VERSION = 2.0
BAUDRATE = 1000000
ADDR_TORQUE_ENABLE = 64
ADDR_OPERATING_MODE = 11
ADDR_GOAL_VELOCITY = 104
ADDR_PRESENT_POSITION = 132
DXL_TICKS_PER_REV = 4096
DYNAMIXEL_SIGNED_32BIT_MAX = 2147483647
DYNAMIXEL_UNSIGNED_32BIT_RANGE = 4294967296
OPERATING_MODE_VELOCITY = 1
VELOCITY_UNIT_RPM = 0.229
DXL_VELOCITY_LIMIT = 330
RAD_PER_SEC_TO_RPM = 60.0 / (2.0 * 3.14159265359)
TICK_TO_RAD = (2.0 * math.pi) / DXL_TICKS_PER_REV

# 수식에서 정의한 바퀴 양의 회전 방향과 실제 다이나믹셀 부호 차이를 보정.
# 현재 하드웨어는 수식 기준과 부호가 반대여서 세 바퀴 모두 -1로 맞춘다.
WHEEL_COMMAND_SIGN_LEFT = -1.0
WHEEL_COMMAND_SIGN_RIGHT = -1.0
WHEEL_COMMAND_SIGN_BACK = -1.0

WHEEL_ENCODER_SIGN_LEFT = -1.0
WHEEL_ENCODER_SIGN_RIGHT = -1.0
WHEEL_ENCODER_SIGN_BACK = -1.0


def _rad_per_sec_to_dxl(rad_s):
    rpm = rad_s * RAD_PER_SEC_TO_RPM
    val = int(rpm / VELOCITY_UNIT_RPM)
    return max(-DXL_VELOCITY_LIMIT, min(DXL_VELOCITY_LIMIT, val))


def _to_signed_32bit(raw_value):
    if raw_value > DYNAMIXEL_SIGNED_32BIT_MAX:
        return raw_value - DYNAMIXEL_UNSIGNED_32BIT_RANGE
    return raw_value


class HanulHardware:
    """실제 한울 로봇: 다이나믹셀 모터(ID 1=오른쪽, 2=뒤, 3=왼쪽)로 옴니휠 제어"""

    def __init__(self, motor_id_left=3, motor_id_right=1, motor_id_back=2, max_speed=6.0, control_hz=50.0,
                 port=None, baudrate=BAUDRATE):
        self.motor_id_left = motor_id_left
        self.motor_id_right = motor_id_right
        self.motor_id_back = motor_id_back
        self.control_hz = control_hz
        self.velocity_controller = OmniVelocityController(max_speed=max_speed, acceleration_factor=0.1)
        self._pos_L = 0.0
        self._pos_R = 0.0
        self._pos_B = 0.0
        self._lidar_connected = False
        self._port_handler = None
        self._packet_handler = None
        port = port or os.environ.get("MOTOR_PORT") or os.environ.get("DXL_PORT")
        if _DXL_AVAILABLE and port:
            ph = PortHandler(port)
            pk = PacketHandler(PROTOCOL_VERSION)
            if ph.openPort():
                ph.setBaudRate(baudrate)
                for dxl_id in (self.motor_id_left, self.motor_id_right, self.motor_id_back):
                    try:
                        pk.write1ByteTxRx(ph, dxl_id, ADDR_OPERATING_MODE, OPERATING_MODE_VELOCITY)
                        time.sleep(0.05)
                        pk.write1ByteTxRx(ph, dxl_id, ADDR_TORQUE_ENABLE, 1)
                    except Exception as e:
                        print("DXL init failed ID %d: %s" % (dxl_id, e))
                        ph.closePort()
                        ph = None
                        pk = None
                        break
                if ph is not None:
                    self._port_handler = ph
                    self._packet_handler = pk
            else:
                self._port_handler = None
                self._packet_handler = None

    def step(self):
        time.sleep(1.0 / self.control_hz)
        return 0

    def set_cmd_vel(self, vx, vy, w):
        vel_L, vel_R, vel_B = self.velocity_controller.update(vx, vy, w)
        self._send_motor_velocity(vel_L, vel_R, vel_B)

    def _send_motor_velocity(self, vel_L, vel_R, vel_B):
        if not _DXL_AVAILABLE or self._packet_handler is None or self._port_handler is None:
            return
        dxl_L = _rad_per_sec_to_dxl(WHEEL_COMMAND_SIGN_LEFT * vel_L)
        dxl_R = _rad_per_sec_to_dxl(WHEEL_COMMAND_SIGN_RIGHT * vel_R)
        dxl_B = _rad_per_sec_to_dxl(WHEEL_COMMAND_SIGN_BACK * vel_B)
        self._packet_handler.write4ByteTxRx(self._port_handler, self.motor_id_left, ADDR_GOAL_VELOCITY, dxl_L)
        self._packet_handler.write4ByteTxRx(self._port_handler, self.motor_id_right, ADDR_GOAL_VELOCITY, dxl_R)
        self._packet_handler.write4ByteTxRx(self._port_handler, self.motor_id_back, ADDR_GOAL_VELOCITY, dxl_B)

    def get_encoder_values(self):
        if not _DXL_AVAILABLE or self._packet_handler is None or self._port_handler is None:
            return (self._pos_L, self._pos_R, self._pos_B)
        try:
            ret_L = self._packet_handler.read4ByteTxRx(self._port_handler, self.motor_id_left, ADDR_PRESENT_POSITION)
            raw_L = ret_L[0] if isinstance(ret_L, (list, tuple)) else ret_L
            res_L = ret_L[1] if isinstance(ret_L, (list, tuple)) and len(ret_L) > 1 else 0
            if res_L == 0:
                self._pos_L = WHEEL_ENCODER_SIGN_LEFT * _to_signed_32bit(raw_L) * TICK_TO_RAD

            ret_R = self._packet_handler.read4ByteTxRx(self._port_handler, self.motor_id_right, ADDR_PRESENT_POSITION)
            raw_R = ret_R[0] if isinstance(ret_R, (list, tuple)) else ret_R
            res_R = ret_R[1] if isinstance(ret_R, (list, tuple)) and len(ret_R) > 1 else 0
            if res_R == 0:
                self._pos_R = WHEEL_ENCODER_SIGN_RIGHT * _to_signed_32bit(raw_R) * TICK_TO_RAD

            ret_B = self._packet_handler.read4ByteTxRx(self._port_handler, self.motor_id_back, ADDR_PRESENT_POSITION)
            raw_B = ret_B[0] if isinstance(ret_B, (list, tuple)) else ret_B
            res_B = ret_B[1] if isinstance(ret_B, (list, tuple)) and len(ret_B) > 1 else 0
            if res_B == 0:
                self._pos_B = WHEEL_ENCODER_SIGN_BACK * _to_signed_32bit(raw_B) * TICK_TO_RAD
        except Exception:
            pass
        return (self._pos_L, self._pos_R, self._pos_B)

    def get_lidar_data(self):
        if not self._lidar_connected:
            return {"ranges": [], "fov": 0.0, "min_range": 0.0, "max_range": 0.0}
        return {"ranges": [], "fov": 0.0, "min_range": 0.0, "max_range": 0.0}

    def stop(self):
        self.velocity_controller.reset()
        self._send_motor_velocity(0.0, 0.0, 0.0)
        if _DXL_AVAILABLE and self._port_handler and self._port_handler.is_open:
            for dxl_id in (self.motor_id_left, self.motor_id_right, self.motor_id_back):
                try:
                    self._packet_handler.write1ByteTxRx(self._port_handler, dxl_id, ADDR_TORQUE_ENABLE, 0)
                except Exception:
                    pass
            self._port_handler.closePort()
