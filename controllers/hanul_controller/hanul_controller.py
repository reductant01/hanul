"""
Hanul 실제 로봇 컨트롤러 진입점
"""
import math
import rclpy

from hanul_hardware import HanulHardware
from common.omni_odometry import OmniOdometry
from common.joint_state_message import create_joint_state_message
from common.odom_message import create_odometry_message
from common.tf_odom_base import create_odometry_transform
from common.tf_base_lidar import TFBaseLidar
from common.lidar_scan_message import LidarScanMessage
from common.tf_map_odom import should_publish_map_odom_identity, create_map_odom_identity
from common.ros_bridge import RobotROSBridge, init_ros_node, shutdown_ros_node

INIT_X = 0.0
INIT_Y = 0.0
INIT_YAW = 0.0

# 실제 로봇의 base_footprint 기준이 RViz/실물 전면과 180도 어긋난 경우,
# NUC 경로에서만 body frame을 통째로 다시 정의한다.
REAL_CMD_SIGN_VX = 1.0
REAL_CMD_SIGN_VY = 1.0
REAL_CMD_SIGN_W = 1.0
REAL_ODOM_YAW_OFFSET = 0.0
REAL_ODOM_TWIST_SIGN_VX = 1.0
REAL_ODOM_TWIST_SIGN_VY = 1.0
REAL_LIDAR_X = -0.085
REAL_LIDAR_Y = 0.0
REAL_LIDAR_Z = 0.113
REAL_LIDAR_YAW = 0.0

def main():
    print("Hanul Controller initializing...")
    robot = HanulHardware()
    print("Real robot hardware (ID L=%s R=%s B=%s) initialized" % (robot.motor_id_left, robot.motor_id_right, robot.motor_id_back))

    odometry = OmniOdometry()
    tf_base_lidar = TFBaseLidar(
        lidar_x=REAL_LIDAR_X,
        lidar_y=REAL_LIDAR_Y,
        lidar_z=REAL_LIDAR_Z,
    )
    lidar_scan_message = LidarScanMessage()
    init_ros_node()
    ros_bridge = RobotROSBridge('hanul_controller_node')
    stamp = ros_bridge.get_clock().now().to_msg()
    ros_bridge.publish_transform(
        create_odometry_transform(
            INIT_X,
            INIT_Y,
            INIT_YAW,
            ros_bridge,
            stamp=stamp,
            yaw_offset=REAL_ODOM_YAW_OFFSET,
        )
    )
    ros_bridge.publish_odom(
        create_odometry_message(
            INIT_X,
            INIT_Y,
            INIT_YAW + REAL_ODOM_YAW_OFFSET,
            ros_bridge,
            stamp=stamp,
        )
    )
    ros_bridge.publish_joint_states(
        create_joint_state_message(
            ros_bridge,
            stamp=stamp,
            names=["joint_wheel_left", "joint_wheel_right", "joint_wheel_back"],
            positions=[0.0, 0.0, 0.0],
        )
    )
    ros_bridge.publish_static_transform(
        tf_base_lidar.create_lidar_transform(
            ros_bridge,
            stamp=stamp,
            lidar_yaw=REAL_LIDAR_YAW,
        )
    )
    print("Hanul Controller ready\n")

    print("Starting main loop. Waiting for /cmd_vel...\n")
    step_count = 0
    log_interval = 1000
    # 실로봇은 라이다/마스킹/SLAM 처리까지 모두 분리 프로세스로 거치므로
    # 50 Hz 그대로 /scan 을 내보내면 slam_toolbox queue가 쉽게 밀린다.
    # scan 주기를 약간 낮춰 처리 여유를 확보한다.
    steps_per_scan_and_identity = 2
    last_stamp_ns = None

    try:
        while rclpy.ok() and robot.step() != -1:
            rclpy.spin_once(ros_bridge, timeout_sec=0)
            vx, vy, w = ros_bridge.get_cmd_vel()
            robot.set_cmd_vel(
                REAL_CMD_SIGN_VX * vx,
                REAL_CMD_SIGN_VY * vy,
                REAL_CMD_SIGN_W * w,
            )
            pos_L, pos_R, pos_B = robot.get_encoder_values()
            delta_x, delta_y, delta_theta = odometry.update(pos_L, pos_R, pos_B)
            x, y, theta = odometry.get_pose()
            x_glob = x + INIT_X
            y_glob = y + INIT_Y
            theta_glob = theta + INIT_YAW
            theta_glob_display = theta_glob + REAL_ODOM_YAW_OFFSET
            stamp = ros_bridge.get_clock().now().to_msg()
            stamp_ns = ros_bridge.get_clock().now().nanoseconds
            dt = 0.0 if last_stamp_ns is None else max((stamp_ns - last_stamp_ns) / 1e9, 1e-6)
            last_stamp_ns = stamp_ns
            odom_vx = 0.0 if dt == 0.0 else (REAL_ODOM_TWIST_SIGN_VX * (delta_x / dt))
            odom_vy = 0.0 if dt == 0.0 else (REAL_ODOM_TWIST_SIGN_VY * (delta_y / dt))
            odom_wz = 0.0 if dt == 0.0 else (delta_theta / dt)
            ros_bridge.publish_transform(
                create_odometry_transform(
                    x_glob,
                    y_glob,
                    theta_glob,
                    ros_bridge,
                    stamp=stamp,
                    yaw_offset=REAL_ODOM_YAW_OFFSET,
                )
            )
            ros_bridge.publish_odom(
                create_odometry_message(
                    x_glob,
                    y_glob,
                    theta_glob_display,
                    ros_bridge,
                    stamp=stamp,
                    linear_x=odom_vx,
                    linear_y=odom_vy,
                    angular_z=odom_wz,
                )
            )
            ros_bridge.publish_joint_states(
                create_joint_state_message(
                    ros_bridge,
                    stamp=stamp,
                    names=["joint_wheel_left", "joint_wheel_right", "joint_wheel_back"],
                    positions=[pos_L, pos_R, pos_B],
                )
            )
            ros_bridge.publish_collision_polygons_rviz(stamp=stamp)
            if step_count % steps_per_scan_and_identity == 0:
                if should_publish_map_odom_identity(x_glob, y_glob, theta_glob):
                    ros_bridge.publish_transform(create_map_odom_identity(ros_bridge, stamp=stamp))
                lidar_data = robot.get_lidar_data()
                scan_msg = lidar_scan_message.create_laser_scan_msg(
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
                print(f"[Step {step_count}] Pos: ({x_glob:.3f}, {y_glob:.3f}), Theta: {theta_glob_display:.3f}")

    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...")

    finally:
        print("Cleaning up...")
        robot.stop()
        shutdown_ros_node()
        print("Shutdown complete")


if __name__ == '__main__':
    main()
