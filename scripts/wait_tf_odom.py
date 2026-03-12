#!/usr/bin/env python3
"""
odom -> base_footprint TF가 나타날 때까지 대기.
Nav2 기동 전에 실행해 costmap이 항상 뜨도록 할 때 사용.

  python3 scripts/wait_tf_odom.py [timeout_sec]
  timeout_sec: 최대 대기 시간(초). 기본 45. 0이면 무한 대기.
  종료 코드: 0 = 변환 확인됨, 1 = 타임아웃/오류
"""
import sys
import time

try:
    import rclpy
    from rclpy.node import Node
    from tf2_ros import Buffer, TransformListener
    from rclpy.duration import Duration
except ImportError:
    print("ROS 2 환경을 먼저 로드하세요: source /opt/ros/jazzy/setup.bash")
    sys.exit(1)


def main():
    timeout_sec = 45.0
    if len(sys.argv) >= 2:
        try:
            timeout_sec = float(sys.argv[1])
        except ValueError:
            pass

    rclpy.init()
    node = Node("wait_tf_odom")
    buffer = Buffer()
    listener = TransformListener(buffer, node)

    target_frame = "odom"
    source_frame = "base_footprint"
    check_interval = 0.2
    deadline = time.monotonic() + timeout_sec if timeout_sec > 0 else None

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=check_interval)
            now = node.get_clock().now()
            try:
                buffer.lookup_transform(
                    target_frame, source_frame, now, Duration(seconds=0)
                )
                node.get_logger().info("odom -> base_footprint OK")
                return 0
            except Exception:
                pass
            if deadline is not None and time.monotonic() >= deadline:
                node.get_logger().warn("Timeout waiting for odom")
                return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
