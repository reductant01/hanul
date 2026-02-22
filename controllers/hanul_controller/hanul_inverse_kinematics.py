"""
역기구학 모듈
로봇의 이동 명령을 모터 속도로 변환합니다.
(vx, vy, w) → (motor_left, motor_right, motor_back)

역기구학 (Inverse Kinematics):
- 입력: 로봇이 가야 할 속도 (vx, vy, w)
- 출력: 각 모터가 돌아야 할 속도
- 역할: 명령 → 모터 제어
"""


class HanulKinematics:
    """3휠 옴니휠 로봇 역기구학 (명령 → 모터)"""
    
    def __init__(self, max_speed=7.0):
        """
        Args:
            max_speed: 최대 모터 속도 (rad/s)
        """
        self.MAX_SPEED = max_speed
    
    def cmd_vel_to_motor_speed(self, vx, vy, w):
        """
        카르테지안 속도를 모터 속도로 변환
        
        3휠 옴니휠의 역기구학:
        motor_left  = (-0.5*vy - 0.866*vx + w) * MAX_SPEED
        motor_right = (-0.5*vy + 0.866*vx + w) * MAX_SPEED
        motor_back  = (1.0*vy + w) * MAX_SPEED
        
        Args:
            vx: 전후 이동 명령 (정규화 값, 일반적으로 [-1, 1])
            vy: 좌우 이동 명령 (정규화 값, 일반적으로 [-1, 1])
            w: 회전 명령 (정규화 값, 일반적으로 [-1, 1])
        
        Returns:
            (motor_left, motor_right, motor_back): 모터 속도 (rad/s)
        """
        # 3휠 옴니휠 로봇의 역기구학 (고정 공식)
        motor_left = (-0.5 * vy - 0.866 * vx + w) * self.MAX_SPEED
        motor_right = (-0.5 * vy + 0.866 * vx + w) * self.MAX_SPEED
        motor_back = (1.0 * vy + w) * self.MAX_SPEED
        
        return self.clamp_speed(motor_left, motor_right, motor_back)
    
    def clamp_speed(self, motor_left, motor_right, motor_back):
        """
        모터 속도를 최대값으로 제한
        
        Args:
            motor_left, motor_right, motor_back: 모터 속도
        
        Returns:
            제한된 모터 속도
        """
        max_vel = max(abs(motor_left), abs(motor_right), abs(motor_back))
        if max_vel > self.MAX_SPEED:
            scale = self.MAX_SPEED / max_vel
            motor_left *= scale
            motor_right *= scale
            motor_back *= scale
        
        return motor_left, motor_right, motor_back
