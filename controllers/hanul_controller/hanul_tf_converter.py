"""
TF (좌표 변환) 메시지 변환 모듈
로봇의 데이터를 ROS TF 메시지로 변환합니다.

역할:
- 오도메트리 데이터 → TF 메시지 변환
- 라이다 센서 데이터 → LaserScan 메시지 변환
- 센서 위치 정보 → TF 메시지 변환

이 모듈은 "메시지 변환"만 담당하고,
실제 발행은 ros_bridge에서 합니다.
"""
from geometry_msgs.msg import TransformStamped
import math


class HanulTFConverter:
    """데이터를 ROS TF 메시지로 변환"""
    
    def __init__(self):
        """로봇의 센서 위치 설정"""
        # worlds/hanul.wbt의 Lidar pose와 동일하게 맞춤
        self.lidar_x = 0.09
        self.lidar_y = 0.0
        self.lidar_z = 0.12375
    
    def create_odometry_transform(self, x, y, theta, ros_node, stamp=None):
        """오도메트리를 TF 메시지로 변환
        
        odom (지도) → base_footprint (로봇)
        
        Args:
            x, y, theta: 로봇의 위치와 각도 (오도메트리에서 계산됨)
            ros_node: ROS 노드 (타임스탬프 생성용)
            stamp: optional, 동일 스탬프를 스캔과 맞출 때 사용
        
        Returns:
            TransformStamped: odom → base_footprint TF 메시지
        """
        t_odom = TransformStamped()
        t_odom.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
        t_odom.header.frame_id = 'odom'           # 기준 좌표계 (지도)
        t_odom.child_frame_id = 'base_footprint'  # 자식 좌표계 (로봇)
        
        t_odom.transform.translation.x = x
        t_odom.transform.translation.y = y
        t_odom.transform.translation.z = 0.0
        
        # 로봇의 회전 (2D 회전을 쿼터니언으로 변환)
        t_odom.transform.rotation.x = 0.0
        t_odom.transform.rotation.y = 0.0
        t_odom.transform.rotation.z = math.sin(theta / 2.0)
        t_odom.transform.rotation.w = math.cos(theta / 2.0)
        
        return t_odom
    
    def create_lidar_transform(self, ros_node):
        """라이다 위치를 TF 메시지로 변환
        
        base_footprint (로봇) → lidar_link (센서)
        
        Args:
            ros_node: ROS 노드 (타임스탬프 생성용)
        
        Returns:
            TransformStamped: base_footprint → lidar_link TF 메시지
        """
        t_lidar = TransformStamped()
        t_lidar.header.stamp = ros_node.get_clock().now().to_msg()
        t_lidar.header.frame_id = 'base_footprint'  # 기준 좌표계 (로봇)
        t_lidar.child_frame_id = 'lidar_link'       # 자식 좌표계 (라이다)
        
        t_lidar.transform.translation.x = self.lidar_x
        t_lidar.transform.translation.y = self.lidar_y
        t_lidar.transform.translation.z = self.lidar_z
        
        t_lidar.transform.rotation.x = 0.0
        t_lidar.transform.rotation.y = 0.0
        t_lidar.transform.rotation.z = 0.0
        t_lidar.transform.rotation.w = 1.0
        
        return t_lidar
    
    def create_laser_scan_msg(self, ranges, fov, min_range, max_range, ros_node, stamp=None):
        """라이다 데이터를 LaserScan 메시지로 변환
        
        Args:
            ranges: 라이다 거리 배열
            fov: 시야각 (라디안)
            min_range: 최소 거리
            max_range: 최대 거리
            ros_node: ROS 노드 (타임스탬프 생성용)
            stamp: optional, odom TF와 동일하게 맞출 때 사용 (lidar_link TF 경고 방지)
        
        Returns:
            LaserScan: 라이다 스캔 메시지
        """
        from sensor_msgs.msg import LaserScan
        
        if not ranges:
            return None
        
        scan_size = len(ranges)
        scan_msg = LaserScan()
        scan_msg.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
        scan_msg.header.frame_id = 'lidar_link'
        scan_msg.angle_min = -fov / 2.0
        if scan_size > 1:
            scan_msg.angle_increment = fov / (scan_size - 1)
        else:
            scan_msg.angle_increment = 0.0
        scan_msg.angle_max = scan_msg.angle_min + scan_msg.angle_increment * (scan_size - 1)
        scan_msg.range_min = min_range
        scan_msg.range_max = max_range
        n = scan_size
        shifted = [ranges[(i + n // 2) % n] for i in range(n)]
        scan_msg.ranges = [shifted[n - 1 - i] for i in range(n)]
        
        return scan_msg
