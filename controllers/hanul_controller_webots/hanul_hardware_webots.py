"""
Webots 시뮬레이터 장치 인터페이스 (모터, 엔코더, 라이다)
"""
from controller import Robot
from common.omni_velocity import OmniVelocityController


class HanulWebots:
    """Webots 시뮬레이터에서 로봇 하드웨어 제어"""

    def __init__(self):
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())

        self.motor_left = self.robot.getDevice("joint_wheel_left")
        self.motor_right = self.robot.getDevice("joint_wheel_right")
        self.motor_back = self.robot.getDevice("joint_wheel_back")

        for motor in [self.motor_left, self.motor_right, self.motor_back]:
            motor.setPosition(float('inf'))
            motor.setVelocity(0.0)

        self.sensor_left = self.robot.getDevice("joint_wheel_left_sensor")
        self.sensor_right = self.robot.getDevice("joint_wheel_right_sensor")
        self.sensor_back = self.robot.getDevice("joint_wheel_back_sensor")

        for sensor in [self.sensor_left, self.sensor_right, self.sensor_back]:
            sensor.enable(self.timestep)

        self.lidar = self.robot.getDevice('lidar a1')
        self.lidar.enable(self.timestep)

        self.velocity_controller = OmniVelocityController(max_speed=6.0, acceleration_factor=0.1)

    def step(self):
        return self.robot.step(self.timestep)

    def set_cmd_vel(self, vx, vy, w):
        vel_L, vel_R, vel_B = self.velocity_controller.update(vx, vy, w)
        self._set_motor_velocity(vel_L, vel_R, vel_B)

    def _set_motor_velocity(self, vel_L, vel_R, vel_B):
        self.motor_left.setVelocity(vel_L)
        self.motor_right.setVelocity(vel_R)
        self.motor_back.setVelocity(vel_B)

    def get_encoder_values(self):
        return (
            self.sensor_left.getValue(),
            self.sensor_right.getValue(),
            self.sensor_back.getValue()
        )

    def get_lidar_data(self):
        return {
            'ranges': self.lidar.getRangeImage(),
            'fov': self.lidar.getFov(),
            'min_range': self.lidar.getMinRange(),
            'max_range': self.lidar.getMaxRange(),
        }

    def stop(self):
        self.velocity_controller.reset()
        self._set_motor_velocity(0.0, 0.0, 0.0)
