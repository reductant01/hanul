"""
Hanul NUC 실제 로봇 컨트롤러 진입점
"""
import rclpy

from hanul_hardware_nuc import HanulHardware
from common.omni_odometry import OmniOdometry
from common.tf_odom_base import create_odometry_transform
from common.tf_base_lidar import TFBaseLidar
from common.tf_lidar_scan import TFLidarScan
from common.tf_map_odom import should_publish_map_odom_identity, create_map_odom_identity
from common.ros_bridge import RobotROSBridge, init_ros_node, shutdown_ros_node

INIT_X = 0.0
INIT_Y = 0.0
INIT_YAW = 0.0

MOTOR_ID_LEFT = 3
MOTOR_ID_RIGHT = 1
MOTOR_ID_BACK = 2


def main():
    print("Hanul NUC Controller initializing...")
    robot = HanulHardware(motor_id_left=MOTOR_ID_LEFT, motor_id_right=MOTOR_ID_RIGHT, motor_id_back=MOTOR_ID_BACK)
    print("Real robot hardware (ID L=%s R=%s B=%s) initialized" % (robot.motor_id_left, robot.motor_id_right, robot.motor_id_back))

    odometry = OmniOdometry()
    tf_base_lidar = TFBaseLidar()
    tf_lidar_scan = TFLidarScan()
    init_ros_node()
    ros_bridge = RobotROSBridge('hanul_controller_node')
    stamp = ros_bridge.get_clock().now().to_msg()
    ros_bridge.publish_transform(create_odometry_transform(INIT_X, INIT_Y, INIT_YAW, ros_bridge, stamp=stamp))
    ros_bridge.publish_transform(tf_base_lidar.create_lidar_transform(ros_bridge, stamp=stamp))
    ros_bridge.publish_transform(tf_base_lidar.create_laser_transform(ros_bridge, stamp=stamp))
    print("Hanul NUC Controller ready\n")

    print("Starting main loop. Waiting for /cmd_vel...\n")
    step_count = 0
    log_interval = 1000
    steps_per_scan_and_identity = 1

    try:
        while rclpy.ok() and robot.step() != -1:
            rclpy.spin_once(ros_bridge, timeout_sec=0)
            vx, vy, w = ros_bridge.get_cmd_vel()
            robot.set_cmd_vel(vx, vy, w)
            pos_L, pos_R, pos_B = robot.get_encoder_values()
            odometry.update(pos_L, pos_R, pos_B)
            x, y, theta = odometry.get_pose()
            x_glob = x + INIT_X
            y_glob = y + INIT_Y
            theta_glob = theta + INIT_YAW
            stamp = ros_bridge.get_clock().now().to_msg()
            ros_bridge.publish_transform(create_odometry_transform(x_glob, y_glob, theta_glob, ros_bridge, stamp=stamp))
            ros_bridge.publish_transform(tf_base_lidar.create_lidar_transform(ros_bridge, stamp=stamp))
            ros_bridge.publish_transform(tf_base_lidar.create_laser_transform(ros_bridge, stamp=stamp))
            ros_bridge.publish_collision_polygons_rviz(stamp=stamp)
            if step_count % steps_per_scan_and_identity == 0:
                if should_publish_map_odom_identity(x_glob, y_glob, theta_glob):
                    ros_bridge.publish_transform(create_map_odom_identity(ros_bridge, stamp=stamp))
                lidar_data = robot.get_lidar_data()
                scan_msg = tf_lidar_scan.create_laser_scan_msg(
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
