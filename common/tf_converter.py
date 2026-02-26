"""
TF (좌표 변환) 및 LaserScan 메시지 변환 모듈
"""
from geometry_msgs.msg import TransformStamped
import math


class TFConverter:
    """오도메트리·라이다 데이터를 ROS TF / LaserScan 메시지로 변환"""

    def __init__(self, lidar_x=0.09, lidar_y=0.0, lidar_z=0.12375):
        self.lidar_x = lidar_x
        self.lidar_y = lidar_y
        self.lidar_z = lidar_z

    def create_odometry_transform(self, x, y, theta, ros_node, stamp=None):
        t_odom = TransformStamped()
        t_odom.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
        t_odom.header.frame_id = 'odom'
        t_odom.child_frame_id = 'base_footprint'

        t_odom.transform.translation.x = x
        t_odom.transform.translation.y = y
        t_odom.transform.translation.z = 0.0

        t_odom.transform.rotation.x = 0.0
        t_odom.transform.rotation.y = 0.0
        t_odom.transform.rotation.z = math.sin(theta / 2.0)
        t_odom.transform.rotation.w = math.cos(theta / 2.0)

        return t_odom

    def create_lidar_transform(self, ros_node):
        t_lidar = TransformStamped()
        t_lidar.header.stamp = ros_node.get_clock().now().to_msg()
        t_lidar.header.frame_id = 'base_footprint'
        t_lidar.child_frame_id = 'lidar_link'

        t_lidar.transform.translation.x = self.lidar_x
        t_lidar.transform.translation.y = self.lidar_y
        t_lidar.transform.translation.z = self.lidar_z

        t_lidar.transform.rotation.x = 0.0
        t_lidar.transform.rotation.y = 0.0
        t_lidar.transform.rotation.z = 0.0
        t_lidar.transform.rotation.w = 1.0

        return t_lidar

    def create_laser_scan_msg(self, ranges, fov, min_range, max_range, ros_node, stamp=None):
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
