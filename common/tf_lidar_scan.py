"""
lidar_link 프레임 LaserScan 메시지 생성. 발행은 ros_bridge.
"""
from sensor_msgs.msg import LaserScan


class TFLidarScan:
    def __init__(self, lidar_range_min=0.05, lidar_range_max=30.0):
        self.lidar_range_min = lidar_range_min
        self.lidar_range_max = lidar_range_max

    def create_laser_scan_msg(self, ranges, fov, min_range, max_range, ros_node, stamp=None):
        if not ranges:
            return None
        scan_size = len(ranges)
        scan_msg = LaserScan()
        scan_msg.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
        scan_msg.header.frame_id = 'lidar_link'
        scan_msg.angle_min = -fov / 2.0
        scan_msg.angle_increment = fov / (scan_size - 1) if scan_size > 1 else 0.0
        scan_msg.angle_max = scan_msg.angle_min + scan_msg.angle_increment * (scan_size - 1)
        scan_msg.range_min = self.lidar_range_min
        scan_msg.range_max = self.lidar_range_max
        scan_msg.ranges = list(ranges)
        return scan_msg
