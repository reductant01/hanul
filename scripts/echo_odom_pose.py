#!/usr/bin/env python3
"""
오도메트리(odom → base_footprint) x, y, theta 출력.
--once: 한 번만 출력하고 종료 (이동 전·후 비교용).
없으면 0.5초마다 계속 출력.

사용법:
  source /opt/ros/jazzy/setup.bash
  python3 scripts/echo_odom_pose.py --once   # 한 번만
  python3 scripts/echo_odom_pose.py          # 계속 출력
"""
import math
import sys

try:
    import rclpy
    from rclpy.node import Node
    from tf2_ros import TransformListener, Buffer
except ImportError:
    print("ROS 2 환경을 먼저 로드하세요: source /opt/ros/jazzy/setup.bash")
    sys.exit(1)


def quat_to_yaw(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny, cosy)


def get_pose_once(node, timeout_sec=1.0):
    t = node.tf_buffer.lookup_transform(
        "odom", "base_footprint", rclpy.time.Time(seconds=0, nanoseconds=0), rclpy.duration.Duration(seconds=timeout_sec)
    )
    x = t.transform.translation.x
    y = t.transform.translation.y
    q = t.transform.rotation
    yaw = quat_to_yaw(q)
    return x, y, yaw


class OdomEcho(Node):
    def __init__(self, use_timer=False):
        super().__init__("echo_odom_pose")
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        if use_timer:
            self.timer = self.create_timer(0.5, self.print_pose)

    def print_pose(self):
        try:
            x, y, yaw = get_pose_once(self)
            print(f"odom → base_footprint  x: {x:7.3f}  y: {y:7.3f}  yaw(deg): {math.degrees(yaw):6.2f}")
        except Exception as e:
            print(f"TF 조회 실패 (odom/base_footprint 없음?): {e}")


def main():
    once = "--once" in sys.argv
    rclpy.init()
    node = OdomEcho(use_timer=not once)
    if once:
        for _ in range(25):
            rclpy.spin_once(node, timeout_sec=0.2)
            try:
                x, y, yaw = get_pose_once(node, timeout_sec=0.5)
                print(f"odom → base_footprint  x: {x:7.3f}  y: {y:7.3f}  yaw(deg): {math.degrees(yaw):6.2f}")
                node.destroy_node()
                if rclpy.ok():
                    rclpy.shutdown()
                return
            except Exception:
                pass
        print("TF 조회 실패: odom/base_footprint 없음. Webots와 로봇 컨트롤러가 떠 있는지 확인하세요.", file=sys.stderr)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        sys.exit(1)
    print("odom pose (0.5초마다). 이동 전·후 값을 기록하세요. Ctrl+C 종료.")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
