#!/usr/bin/env python3
"""
/initialpose로 초기 포즈 한 번 발행. RViz 2D Pose Estimate를 코드로 대신.
loc 모드에서 Nav2 기동 후 실행.

사용법:
  python3 scripts/amcl_pose_estimate.py
      → AMCL 현재 추정을 /initialpose로 전송 (기본 동작)
  python3 scripts/amcl_pose_estimate.py --origin [x [y [yaw]]]
      → 고정 포즈 (기본 0, 0, 0°) 전송. hanul_webots.sh 첫 기동 시 사용.
  python3 scripts/amcl_pose_estimate.py 1.0 0.5 [yaw]
      → 고정 포즈 (1, 0.5) 또는 (1, 0.5, yaw) 전송.
"""
import sys
import math
import time

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
    from geometry_msgs.msg import PoseWithCovarianceStamped
except ImportError:
    print("ROS 2 환경을 먼저 로드하세요: source /opt/ros/jazzy/setup.bash")
    sys.exit(1)

INITIAL_POSE_TOPIC = "initialpose"
AMCL_POSE_TOPICS = ["/amcl_pose", "/localization/amcl_pose"]
WAIT_TIMEOUT_SEC = 5.0

DEFAULT_COVARIANCE = [
    0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0685,
]


def _parse_fixed_args(args):
    x, y, yaw = 0.0, 0.0, 0.0
    if len(args) >= 2:
        try:
            x = float(args[0])
            y = float(args[1])
            yaw = float(args[2]) if len(args) >= 3 else 0.0
        except ValueError:
            pass
    return x, y, yaw


def main():
    argv = sys.argv[1:]
    use_amcl_current = True
    fixed_args = []

    if argv and argv[0] in ("--origin", "-o"):
        use_amcl_current = False
        fixed_args = argv[1:]
    elif argv and argv[0] in ("--current", "-c"):
        use_amcl_current = True
    elif len(argv) >= 2:
        use_amcl_current = False
        fixed_args = argv
    elif argv:
        use_amcl_current = False

    rclpy.init()
    node = Node("amcl_pose_estimate")
    pub = node.create_publisher(PoseWithCovarianceStamped, "/" + INITIAL_POSE_TOPIC, 10)

    if use_amcl_current:
        amcl_received = [None]

        def make_cb():
            def cb(msg):
                if amcl_received[0] is None:
                    amcl_received[0] = msg
            return cb

        qos_reliable = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
        )
        qos_best_effort = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
        )
        for topic in AMCL_POSE_TOPICS:
            node.create_subscription(PoseWithCovarianceStamped, topic, make_cb(), qos_reliable)
            node.create_subscription(PoseWithCovarianceStamped, topic, make_cb(), qos_best_effort)
        time.sleep(1.0)
        node.get_logger().info("Waiting for AMCL pose (timeout %.1fs)..." % WAIT_TIMEOUT_SEC)
        deadline = time.monotonic() + WAIT_TIMEOUT_SEC
        while rclpy.ok() and amcl_received[0] is None and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        if amcl_received[0] is None:
            node.get_logger().error(
                "No AMCL pose. Ensure loc mode is running and initial pose was set once (e.g. Init Pose panel or amcl_pose_estimate.py). "
                "If AMCL cannot process scans (e.g. lidar_link TF timing), it may not publish; see docs/hanul/04_navigation.md (map->odom identity)."
            )
            node.destroy_node()
            rclpy.shutdown()
            return 1
        msg = amcl_received[0]
        msg.header.stamp = node.get_clock().now().to_msg()
        pub.publish(msg)
        p = msg.pose.pose.position
        o = msg.pose.pose.orientation
        yaw = 2.0 * math.atan2(o.z, o.w)
        node.get_logger().info(
            "Initial pose from AMCL (%.2f, %.2f, yaw=%.3f) sent to /%s" % (p.x, p.y, yaw, INITIAL_POSE_TOPIC)
        )
        node.destroy_node()
        rclpy.shutdown()
        return 0

    x, y, yaw = _parse_fixed_args(fixed_args)

    msg = PoseWithCovarianceStamped()
    msg.header.frame_id = "map"
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.pose.pose.position.x = x
    msg.pose.pose.position.y = y
    msg.pose.pose.position.z = 0.0
    msg.pose.pose.orientation.x = 0.0
    msg.pose.pose.orientation.y = 0.0
    msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
    msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
    msg.pose.covariance = DEFAULT_COVARIANCE

    time.sleep(0.5)
    pub.publish(msg)
    node.get_logger().info("Initial pose (%.2f, %.2f, yaw=%.3f) sent to /%s" % (x, y, yaw, INITIAL_POSE_TOPIC))
    time.sleep(0.3)
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
