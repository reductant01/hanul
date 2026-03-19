#!/usr/bin/env python3
"""
/scan_raw 를 받아 지정한 각도 범위만 남기고 /scan 으로 다시 발행한다.
범위 밖의 빔은 inf 로 바꿔 SLAM/Nav2 에서 벽으로 쓰지 않도록 한다.
"""
import copy
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarScanMask(Node):
    def __init__(self):
        super().__init__("lidar_scan_mask")

        self.declare_parameter("input_topic", "/scan_raw")
        self.declare_parameter("output_topic", "/scan")
        self.declare_parameter("keep_lower_angle_deg", -120.0)
        self.declare_parameter("keep_upper_angle_deg", 120.0)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        keep_lower_angle_deg = self.get_parameter("keep_lower_angle_deg").get_parameter_value().double_value
        keep_upper_angle_deg = self.get_parameter("keep_upper_angle_deg").get_parameter_value().double_value

        self.keep_lower_angle = math.radians(keep_lower_angle_deg)
        self.keep_upper_angle = math.radians(keep_upper_angle_deg)

        self.publisher = self.create_publisher(LaserScan, output_topic, 10)
        self.subscription = self.create_subscription(LaserScan, input_topic, self._on_scan, 10)

        self.get_logger().info(
            "Masking %s -> %s, keeping %.1fdeg .. %.1fdeg"
            % (input_topic, output_topic, keep_lower_angle_deg, keep_upper_angle_deg)
        )

    def _on_scan(self, msg):
        masked = copy.deepcopy(msg)
        ranges = list(masked.ranges)

        if not ranges:
            self.publisher.publish(masked)
            return

        for index in range(len(ranges)):
            angle = msg.angle_min + (msg.angle_increment * index)
            if angle < self.keep_lower_angle or angle > self.keep_upper_angle:
                ranges[index] = float("inf")

        masked.ranges = ranges
        self.publisher.publish(masked)


def main():
    rclpy.init()
    node = LidarScanMask()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
