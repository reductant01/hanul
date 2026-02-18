"""
오도메트리 계산 모듈
3휠 옴니 휠 로봇의 위치와 각도를 계산합니다.
"""
import math


class HanulOdometry:
    """3휠 옴니휠 로봇 오도메트리"""
    
    def __init__(self, wheel_radius=0.05, wheelbase=0.1328):
        """
        Args:
            wheel_radius: 바퀴 반지름 (m)
            wheelbase: 바퀴 간 거리 (m)
        """
        self.R = wheel_radius      # 바퀴 반지름
        self.L = wheelbase         # 바퀴 간 거리
        
        # 누적 위치
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  # 라디안
        
        # 이전 엔코더 값
        self.last_pos_L = 0.0
        self.last_pos_R = 0.0
        self.last_pos_B = 0.0
    
    def update(self, pos_L, pos_R, pos_B):
        """
        엔코더 값으로 오도메트리 업데이트
        
        Args:
            pos_L: 왼쪽 바퀴 엔코더 (라디안)
            pos_R: 오른쪽 바퀴 엔코더 (라디안)
            pos_B: 뒤 바퀴 엔코더 (라디안)
        
        Returns:
            (delta_x, delta_y, delta_theta): 이동량
        """
        # 엔코더 변화량
        delta_L = (pos_L - self.last_pos_L) * self.R
        delta_R = (pos_R - self.last_pos_R) * self.R
        delta_B = (pos_B - self.last_pos_B) * self.R
        
        # 노이즈 제거 (미세 진동)
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
        
        # 순기학 (Forward Kinematics) 사용 (엔코더값 → 로봇 위치)
        # 각 바퀴의 이동거리 → 로봇의 이동량 
        delta_x = (delta_R - delta_L) / 1.73205  # √3 으로 나눔
        delta_y = (delta_L + delta_R - 2.0 * delta_B) / 3.0
        delta_theta = (delta_L + delta_R + delta_B) / (3.0 * self.L)
        
        # 현재 위치 업데이트 (회전을 고려한 좌표 변환)
        avg_theta = self.theta + (delta_theta / 2.0)
        self.x += (delta_x * math.cos(avg_theta) - delta_y * math.sin(avg_theta))
        self.y += (delta_x * math.sin(avg_theta) + delta_y * math.cos(avg_theta))
        self.theta += delta_theta
        
        # 각도 정규화 (-π ~ π)
        while self.theta > math.pi:
            self.theta -= 2.0 * math.pi
        while self.theta < -math.pi:
            self.theta += 2.0 * math.pi
        
        return delta_x, delta_y, delta_theta
    
    def get_pose(self):
        """현재 위치와 각도 반환"""
        return self.x, self.y, self.theta
    
    def reset(self):
        """오도메트리 초기화"""
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_pos_L = 0.0
        self.last_pos_R = 0.0
        self.last_pos_B = 0.0
