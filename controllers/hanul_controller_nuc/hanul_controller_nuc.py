"""
Hanul NUC 실제 로봇 컨트롤러 진입점
"""
import rclpy

from hanul_hardware_nuc import HanulHardware
from common.omni_odometry import OmniOdometry
from common.tf_converter import TFConverter
from common.ros_bridge import RobotROSBridge, init_ros_node, shutdown_ros_node


def main():
    print("Hanul NUC Controller initializing...")
    robot = HanulHardware(motor_id_left=3, motor_id_right=1, motor_id_back=2)
    print("Real robot hardware (ID L=%s R=%s B=%s) initialized" % (robot.motor_id_left, robot.motor_id_right, robot.motor_id_back))

    odometry = OmniOdometry()
    tf_converter = TFConverter()
    init_ros_node()
    ros_bridge = RobotROSBridge('hanul_controller_node')
    print("Hanul NUC Controller ready\n")

    print("Starting main loop. Waiting for /cmd_vel...\n")
    step_count = 0
    log_interval = 1000

    t_lidar_static = tf_converter.create_lidar_transform(ros_bridge)
    ros_bridge.publish_static_transform(t_lidar_static)
    t_laser_static = tf_converter.create_laser_transform(ros_bridge)
    ros_bridge.publish_static_transform(t_laser_static)

    try:
        while rclpy.ok() and robot.step() != -1:
            rclpy.spin_once(ros_bridge, timeout_sec=0)
            vx, vy, w = ros_bridge.get_cmd_vel()
            robot.set_cmd_vel(vx, vy, w)
            pos_L, pos_R, pos_B = robot.get_encoder_values()
            odometry.update(pos_L, pos_R, pos_B)
            x, y, theta = odometry.get_pose()
            stamp = ros_bridge.get_clock().now().to_msg()
            t_lidar_static.header.stamp = stamp
            t_laser_static.header.stamp = stamp
            ros_bridge.publish_static_transform(t_lidar_static)
            ros_bridge.publish_static_transform(t_laser_static)
            t_odom = tf_converter.create_odometry_transform(
                x, y, theta, ros_bridge, stamp=stamp
            )
            ros_bridge.publish_transform(t_odom)
            lidar_data = robot.get_lidar_data()
            scan_msg = tf_converter.create_laser_scan_msg(
                lidar_data['ranges'],
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
