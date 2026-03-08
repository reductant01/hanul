#!/usr/bin/env python3
"""
AMCL 추정을 반영해 /initialpose로 포즈를 한 번 발행.
RViz 2D Pose Estimate를 코드로 대신. loc 모드에서 Nav2 기동 후 실행.

사용법:
  python3 scripts/amcl_pose_estimate.py --current   # AMCL 현재 추정을 /initialpose로 전송 (2D Pose Estimate 대체)
  python3 scripts/amcl_pose_estimate.py              # (0, 0, 0°)
  python3 scripts/amcl_pose_estimate.py 1.0 0.5     # (1, 0.5), 방향 0°
  python3 scripts/amcl_pose_estimate.py 1.0 0.5 0.785  # (1, 0.5), yaw 0.785 rad
"""
import sys
import math
import time

try:
    import rclpy
    from rclpy.node import Node
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


def main():
    use_current = len(sys.argv) >= 2 and sys.argv[1] in ("--current", "-c")
    args = [a for a in sys.argv[1:] if a not in ("--current", "-c")]

    rclpy.init()
    node = Node("amcl_pose_estimate")
    pub = node.create_publisher(PoseWithCovarianceStamped, "/" + INITIAL_POSE_TOPIC, 10)

    if use_current:
        amcl_received = [None]

        def make_cb():
            def cb(msg):
                if amcl_received[0] is None:
                    amcl_received[0] = msg
            return cb

        for topic in AMCL_POSE_TOPICS:
            node.create_subscription(PoseWithCovarianceStamped, topic, make_cb(), 10)
        node.get_logger().info("Waiting for AMCL pose (timeout %.1fs)..." % WAIT_TIMEOUT_SEC)
        deadline = time.monotonic() + WAIT_TIMEOUT_SEC
        while rclpy.ok() and amcl_received[0] is None and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        if amcl_received[0] is None:
            node.get_logger().error(
                "No AMCL pose. Ensure loc mode is running and initial pose was set once (e.g. Init Pose panel or amcl_pose_estimate.py)."
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

    x = 0.0
    y = 0.0
    yaw = 0.0
    if len(args) >= 2:
        try:
            x = float(args[0])
            y = float(args[1])
            if len(args) >= 3:
                yaw = float(args[2])
        except ValueError:
            pass

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
