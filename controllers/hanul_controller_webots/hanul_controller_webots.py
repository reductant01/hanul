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
from common.tf_map_odom import should_publish_map_odom_identity, create_map_odom_identity
from common.ros_bridge import RobotROSBridge, init_ros_node, shutdown_ros_node

INIT_X = 0.0
INIT_Y = 0.0
INIT_YAW = 0.0


def main():
    print("Hanul Webots Controller initializing...")
    robot = HanulWebots()
    print("Webots interface initialized")

    odometry = OmniOdometry()
    tf_converter = TFConverter()
    init_ros_node()
    ros_bridge = RobotROSBridge('hanul_controller_node')
    stamp = ros_bridge.get_clock().now().to_msg()
    ros_bridge.publish_transform(tf_converter.create_odometry_transform(INIT_X, INIT_Y, INIT_YAW, ros_bridge, stamp=stamp, yaw_offset=0.0))
    ros_bridge.publish_transform(tf_converter.create_lidar_transform(ros_bridge, stamp=stamp, lidar_yaw=math.pi))
    print("Hanul Webots Controller ready\n")

    print("Starting main loop. Waiting for /cmd_vel...\n")
    step_count = 0
    log_interval = 1000
    steps_per_scan_and_identity = 8

    try:
        while rclpy.ok() and robot.step() != -1:
            rclpy.spin_once(ros_bridge, timeout_sec=0)
            stamp = ros_bridge.get_clock().now().to_msg()
            vx, vy, w = ros_bridge.get_cmd_vel()
            robot.set_cmd_vel(-vx, -vy, -w)
            pos_L, pos_R, pos_B = robot.get_encoder_values()
            odometry.update(pos_L, pos_R, pos_B)
            x, y, theta = odometry.get_pose()
            x_glob = x + INIT_X
            y_glob = y + INIT_Y
            theta_glob = theta + INIT_YAW
            t_odom = tf_converter.create_odometry_transform(
                x_glob, y_glob, theta_glob, ros_bridge, stamp=stamp, yaw_offset=0.0
            )
            ros_bridge.publish_transform(t_odom)
            t_lidar = tf_converter.create_lidar_transform(ros_bridge, stamp=stamp, lidar_yaw=math.pi)
            ros_bridge.publish_transform(t_lidar)
            ros_bridge.publish_collision_polygons_rviz(stamp=stamp)
            if step_count % steps_per_scan_and_identity == 0:
                if should_publish_map_odom_identity(x_glob, y_glob, theta_glob):
                    ros_bridge.publish_transform(create_map_odom_identity(ros_bridge, stamp=stamp))
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
                print(f"[Step {step_count}] Pos: ({x_glob:.3f}, {y_glob:.3f}), Theta: {theta_glob:.3f}")

    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...")

    finally:
        print("Cleaning up...")
        robot.stop()
        shutdown_ros_node()
        print("Shutdown complete")


if __name__ == '__main__':
    main()
