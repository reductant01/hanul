"""
Hanul Webots 컨트롤러 진입점
"""
import sys
import os

_ros_python = "/opt/ros/jazzy/lib/python3.12/site-packages"
if os.path.exists(_ros_python) and _ros_python not in sys.path:
    sys.path.insert(0, _ros_python)
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import math
import rclpy

from hanul_hardware_webots import HanulWebots
from common.omni_odometry import OmniOdometry
from common.tf_converter import TFConverter
from common.ros_bridge import RobotROSBridge, init_ros_node, shutdown_ros_node


def main():
    print("Hanul Webots Controller initializing...")
    robot = HanulWebots()
    print("Webots interface initialized")

    odometry = OmniOdometry()
    tf_converter = TFConverter()
    init_ros_node()
    ros_bridge = RobotROSBridge('hanul_controller_node')
    stamp = ros_bridge.get_clock().now().to_msg()
    ros_bridge.publish_transform(tf_converter.create_odometry_transform(0.0, 0.0, 0.0, ros_bridge, stamp=stamp, yaw_offset=0.0))
    ros_bridge.publish_transform(tf_converter.create_lidar_transform(ros_bridge, stamp=stamp, lidar_yaw=math.pi))
    print("Hanul Webots Controller ready\n")

    print("Starting main loop. Waiting for /cmd_vel...\n")
    step_count = 0
    log_interval = 1000
    scan_throttle = 8

    try:
        while rclpy.ok() and robot.step() != -1:
            rclpy.spin_once(ros_bridge, timeout_sec=0)
            stamp = ros_bridge.get_clock().now().to_msg()
            vx, vy, w = ros_bridge.get_cmd_vel()
            robot.set_cmd_vel(-vx, -vy, -w)
            pos_L, pos_R, pos_B = robot.get_encoder_values()
            odometry.update(pos_L, pos_R, pos_B)
            x, y, theta = odometry.get_pose()
            t_odom = tf_converter.create_odometry_transform(
                x, y, theta, ros_bridge, stamp=stamp, yaw_offset=0.0
            )
            ros_bridge.publish_transform(t_odom)
            t_lidar = tf_converter.create_lidar_transform(ros_bridge, stamp=stamp, lidar_yaw=math.pi)
            ros_bridge.publish_transform(t_lidar)
            if step_count % scan_throttle == 0:
                ros_bridge.publish_transform(tf_converter.create_map_odom_identity(ros_bridge, stamp=stamp))
                lidar_data = robot.get_lidar_data()
                scan_msg = tf_converter.create_laser_scan_msg(
                    lidar_data['ranges'][::-1],
                    lidar_data['fov'],
                    lidar_data['min_range'],
                    lidar_data['max_range'],
                    ros_bridge,
                    stamp=stamp,
                )
                if scan_msg:
                    ros_bridge.publish_scan(scan_msg)

            step_count += 1
            if step_count % log_interval == 0:
                print(f"[Step {step_count}] Pos: ({x:.3f}, {y:.3f}), Theta: {theta:.3f}")

    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...")

    finally:
        print("Cleaning up...")
        robot.stop()
        shutdown_ros_node()
        print("Shutdown complete")


if __name__ == '__main__':
    main()
