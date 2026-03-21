#!/usr/bin/env python3
"""
/scan_raw 를 받아 지정한 각도 구간을 마스킹하고 /scan 으로 다시 발행한다.
마스킹된 빔은 inf 로 바꿔 SLAM/Nav2 에서 벽으로 쓰지 않도록 한다.
"""
import copy
import math

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import LaserScan


class LidarScanMask(Node):
    def __init__(self):
        super().__init__("lidar_scan_mask")

        self.declare_parameter("input_topic", "/scan_raw")
        self.declare_parameter("output_topic", "/scan")
        self.declare_parameter("mask_lower_angle_deg", -60.0)
        self.declare_parameter("mask_upper_angle_deg", 60.0)
        self.declare_parameter("restamp_output", True)
        self.declare_parameter("publish_every_n", 1)
        self.declare_parameter("restamp_offset_sec", 0.05)

        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value
        mask_lower_angle_deg = self.get_parameter("mask_lower_angle_deg").get_parameter_value().double_value
        mask_upper_angle_deg = self.get_parameter("mask_upper_angle_deg").get_parameter_value().double_value
        self.restamp_output = self.get_parameter("restamp_output").get_parameter_value().bool_value
        self.publish_every_n = max(1, self.get_parameter("publish_every_n").get_parameter_value().integer_value)
        self.restamp_offset_sec = max(0.0, self.get_parameter("restamp_offset_sec").get_parameter_value().double_value)
        self.scan_count = 0

        self.mask_lower_angle = math.radians(mask_lower_angle_deg)
        self.mask_upper_angle = math.radians(mask_upper_angle_deg)

        self.publisher = self.create_publisher(LaserScan, output_topic, 10)
        self.subscription = self.create_subscription(LaserScan, input_topic, self._on_scan, 10)

        self.get_logger().info(
            "Masking %s -> %s, removing %.1fdeg .. %.1fdeg (restamp=%s, offset=%.3fs, every_n=%d)"
            % (
                input_topic,
                output_topic,
                mask_lower_angle_deg,
                mask_upper_angle_deg,
                self.restamp_output,
                self.restamp_offset_sec,
                self.publish_every_n,
            )
        )

    @staticmethod
    def _normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def _is_masked_angle(self, angle):
        angle = self._normalize_angle(angle)
        lower = self._normalize_angle(self.mask_lower_angle)
        upper = self._normalize_angle(self.mask_upper_angle)

        if lower <= upper:
            return lower <= angle <= upper
        return angle >= lower or angle <= upper

    def _on_scan(self, msg):
        self.scan_count += 1
        if self.scan_count % self.publish_every_n != 0:
            return

        masked = copy.deepcopy(msg)
        if self.restamp_output:
            stamp = self.get_clock().now()
            if self.restamp_offset_sec > 0.0:
                stamp = stamp - Duration(seconds=self.restamp_offset_sec)
            masked.header.stamp = stamp.to_msg()
        ranges = list(masked.ranges)

        if not ranges:
            self.publisher.publish(masked)
            return

        for index in range(len(ranges)):
            angle = msg.angle_min + (msg.angle_increment * index)
            if self._is_masked_angle(angle):
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
