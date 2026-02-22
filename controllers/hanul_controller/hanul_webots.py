"""
Webots 시뮬레이터 인터페이스
모터, 센서, 라이다 등 Webots 장치 제어만 담당합니다.
이 파일은 Webots 전용이며, 실제 로봇에서는 사용할 수 없습니다.
"""
from controller import Robot
from hanul_inverse_kinematics import HanulKinematics


class HanulWebots:
    """Webots 시뮬레이터에서 로봇 하드웨어 제어"""
    
    def __init__(self):
        # Webots 로봇 초기화
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        
        # 모터 설정
        self.motor_left = self.robot.getDevice("joint_wheel_left")
        self.motor_right = self.robot.getDevice("joint_wheel_right")
        self.motor_back = self.robot.getDevice("joint_wheel_back")
        
        for motor in [self.motor_left, self.motor_right, self.motor_back]:
            motor.setPosition(float('inf'))  # 무한 회전 모드
            motor.setVelocity(0.0)
        
        # 엔코더 설정
        self.sensor_left = self.robot.getDevice("joint_wheel_left_sensor")
        self.sensor_right = self.robot.getDevice("joint_wheel_right_sensor")
        self.sensor_back = self.robot.getDevice("joint_wheel_back_sensor")
        
        for sensor in [self.sensor_left, self.sensor_right, self.sensor_back]:
            sensor.enable(self.timestep)
        
        # 라이다 설정
        self.lidar = self.robot.getDevice('lidar a1')
        self.lidar.enable(self.timestep)
        
        # 역기구학 모듈
        self.kinematics = HanulKinematics(max_speed=6.0)
        
        # 가속도 제한 파라미터
        self.acceleration_factor = 0.1  # 부드러운 가속
        
        # 현재 모터 속도 (가속도 제한용)
        self.current_vel_L = 0.0
        self.current_vel_R = 0.0
        self.current_vel_B = 0.0
    
    def step(self):
        """시뮬레이션 1 타임스텝 진행"""
        return self.robot.step(self.timestep)
    
    def set_cmd_vel(self, vx, vy, w):
        """속도 명령 설정
        
        Args:
            vx: 전후 선속도 (m/s)
            vy: 좌우 선속도 (m/s)
            w: 각속도 (rad/s)
        """
        # 1️⃣ 역기구학으로 목표 모터 속도 계산
        target_vel_left, target_vel_right, target_vel_back = \
            self.kinematics.cmd_vel_to_motor_speed(vx, vy, w)
        
        # 2️⃣ 부드러운 가속 (급격한 변화 방지)
        self.current_vel_L += self.acceleration_factor * (target_vel_left - self.current_vel_L)
        self.current_vel_R += self.acceleration_factor * (target_vel_right - self.current_vel_R)
        self.current_vel_B += self.acceleration_factor * (target_vel_back - self.current_vel_B)
        
        # 3️⃣ 모터에 속도 설정 (실제 제어)
        self._set_motor_velocity(self.current_vel_L, self.current_vel_R, self.current_vel_B)
    
    def _set_motor_velocity(self, vel_L, vel_R, vel_B):
        """모터에 속도 설정
        
        Args:
            vel_L, vel_R, vel_B: 모터 속도 (rad/s)
        """
        self.motor_left.setVelocity(vel_L)
        self.motor_right.setVelocity(vel_R)
        self.motor_back.setVelocity(vel_B)
    
    def get_encoder_values(self):
        """현재 엔코더 값 반환
        
        Returns:
            (pos_L, pos_R, pos_B): 각 바퀴의 엔코더 값 (라디안)
        """
        return (
            self.sensor_left.getValue(),
            self.sensor_right.getValue(),
            self.sensor_back.getValue()
        )
    
    def get_lidar_data(self):
        """라이다 데이터 반환"""
        return {
            'ranges': self.lidar.getRangeImage(),
            'fov': self.lidar.getFov(),
            'min_range': self.lidar.getMinRange(),
            'max_range': self.lidar.getMaxRange(),
        }
    
    def stop(self):
        """모터 정지"""
        self.set_cmd_vel(0.0, 0.0, 0.0)
