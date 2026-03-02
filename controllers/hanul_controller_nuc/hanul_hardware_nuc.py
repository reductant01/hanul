"""
NUC 실제 로봇 하드웨어 인터페이스 (다이나믹셀 ID 1=오른쪽, 2=뒤, 3=왼쪽)
"""
import os
import time
from common.omni_velocity import OmniVelocityController

try:
    from dynamixel_sdk import PortHandler, PacketHandler  # type: ignore[reportMissingImports]
    _DXL_AVAILABLE = True
except ImportError:
    _DXL_AVAILABLE = False

PROTOCOL_VERSION = 2.0
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_VELOCITY = 104
ADDR_PRESENT_POSITION = 132
VELOCITY_UNIT_RPM = 0.229
RAD_PER_SEC_TO_RPM = 60.0 / (2.0 * 3.14159265359)


def _rad_per_sec_to_dxl(rad_s):
    rpm = rad_s * RAD_PER_SEC_TO_RPM
    val = int(rpm / VELOCITY_UNIT_RPM)
    return max(-1023, min(1023, val))


class HanulHardware:
    """실제 한울 로봇: 다이나믹셀 모터(ID 1=오른쪽, 2=뒤, 3=왼쪽)로 옴니휠 제어"""

    def __init__(self, motor_id_left=3, motor_id_right=1, motor_id_back=2, max_speed=6.0, control_hz=50.0,
                 port=None, baudrate=1000000):
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
                        pk.write1ByteTxRx(ph, dxl_id, ADDR_TORQUE_ENABLE, 1)
                    except Exception:
                        ph.closePort()
                        ph = None
                        pk = None
                        break
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
        dxl_L = _rad_per_sec_to_dxl(vel_L)
        dxl_R = _rad_per_sec_to_dxl(vel_R)
        dxl_B = _rad_per_sec_to_dxl(vel_B)
        self._packet_handler.write4ByteTxRx(self._port_handler, self.motor_id_left, ADDR_GOAL_VELOCITY, dxl_L)
        self._packet_handler.write4ByteTxRx(self._port_handler, self.motor_id_right, ADDR_GOAL_VELOCITY, dxl_R)
        self._packet_handler.write4ByteTxRx(self._port_handler, self.motor_id_back, ADDR_GOAL_VELOCITY, dxl_B)

    def get_encoder_values(self):
        if not _DXL_AVAILABLE or self._packet_handler is None or self._port_handler is None:
            return (self._pos_L, self._pos_R, self._pos_B)
        try:
            self._pos_L = self._packet_handler.read4ByteTxRx(self._port_handler, self.motor_id_left, ADDR_PRESENT_POSITION)[0]
            self._pos_R = self._packet_handler.read4ByteTxRx(self._port_handler, self.motor_id_right, ADDR_PRESENT_POSITION)[0]
            self._pos_B = self._packet_handler.read4ByteTxRx(self._port_handler, self.motor_id_back, ADDR_PRESENT_POSITION)[0]
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
        if _DXL_AVAILABLE and self._port_handler and self._port_handler.isOpen():
            for dxl_id in (self.motor_id_left, self.motor_id_right, self.motor_id_back):
                try:
                    self._packet_handler.write1ByteTxRx(self._port_handler, dxl_id, ADDR_TORQUE_ENABLE, 0)
                except Exception:
                    pass
            self._port_handler.closePort()
