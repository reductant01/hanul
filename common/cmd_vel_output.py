#!/usr/bin/env python3
"""
구독: cmd_vel_filtered, cmd_vel_unfiltered(텔레옵), cmd_vel_nav(Nav2).  발행: cmd_vel (단일 출처)
Nav2 활성 시 cmd_vel_nav를 cmd_vel로 그대로 전달; 비활성 시 텔레옵 파이프라인(후진 탈출 로직 포함) 사용.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


def _is_zero(t: Twist, eps=1e-3):
    return (
        abs(t.linear.x) <= eps
        and abs(t.linear.y) <= eps
        and abs(t.linear.z) <= eps
        and abs(t.angular.x) <= eps
        and abs(t.angular.y) <= eps
        and abs(t.angular.z) <= eps
    )


def _is_backward(t: Twist, thresh=0.01):
    return t.linear.x < -thresh


class CmdVelOutputNode(Node):
    def __init__(self):
        super().__init__("cmd_vel_output")
        self._safe = None
        self._requested = None
        self._safe_ok = False
        self._requested_ok = False
        self._have_seen_nonzero_safe = False
        self._last_nav_time_ns = None
        self._last_nav_msg = None
        self.declare_parameter("backward_escape_linear_threshold", 0.01)
        self.declare_parameter("nav_active_timeout_sec", 0.4)
        self._back_thresh = self.get_parameter("backward_escape_linear_threshold").value
        self._nav_timeout_ns = int(self.get_parameter("nav_active_timeout_sec").value * 1e9)
        self.create_subscription(Twist, "cmd_vel_filtered", self._cb_safe, 10)
        self.create_subscription(Twist, "cmd_vel_unfiltered", self._cb_requested, 10)
        self.create_subscription(Twist, "cmd_vel_nav", self._cb_nav, 10)
        self._pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_timer(0.05, self._publish)
        self.get_logger().info("cmd_vel_output started (teleop via filter; Nav2 bypass when cmd_vel_nav active).")

    def _cb_safe(self, msg):
        self._safe = msg
        self._safe_ok = True
        if not _is_zero(msg):
            self._have_seen_nonzero_safe = True

    def _cb_requested(self, msg):
        self._requested = msg
        self._requested_ok = True

    def _cb_nav(self, msg):
        self._last_nav_time_ns = self.get_clock().now().nanoseconds
        self._last_nav_msg = msg

    def _nav_active(self):
        if self._last_nav_time_ns is None:
            return False
        return (self.get_clock().now().nanoseconds - self._last_nav_time_ns) < self._nav_timeout_ns

    def _publish(self):
        if self._nav_active() and self._last_nav_msg is not None:
            self._pub.publish(self._last_nav_msg)
            return
        out = Twist()
        if not self._safe_ok:
            if self._requested_ok and self._requested:
                out = self._requested
            self._pub.publish(out)
            return
        if self._safe is not None and _is_zero(self._safe):
            if (
                self._have_seen_nonzero_safe
                and self._requested_ok
                and self._requested
                and not _is_zero(self._requested)
            ):
                if _is_backward(self._requested, self._back_thresh):
                    out = self._requested
            else:
                out = self._requested if (self._requested_ok and self._requested) else self._safe
        else:
            out = self._safe if self._safe else Twist()
        self._pub.publish(out)


def main():
    rclpy.init()
    node = CmdVelOutputNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
