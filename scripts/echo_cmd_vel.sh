#!/usr/bin/env bash
# /cmd_vel_nav -> /cmd_vel -> /cmd_vel_to_robot 흐름을 한 화면에서 비교.
# Ctrl+C 종료.
set -euo pipefail
source /opt/ros/jazzy/setup.bash

python3 - <<'PY'
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


def fmt_twist(msg):
    return (
        f"x={msg.linear.x:+.3f} "
        f"y={msg.linear.y:+.3f} "
        f"w={msg.angular.z:+.3f}"
    )


class CmdVelMonitor(Node):
    def __init__(self):
        super().__init__("cmd_vel_monitor")
        self.latest = {
            "/cmd_vel_nav": None,
            "/cmd_vel": None,
            "/cmd_vel_to_robot": None,
        }
        self.create_subscription(Twist, "/cmd_vel_nav", self._cb_nav, 10)
        self.create_subscription(Twist, "/cmd_vel", self._cb_cmd, 10)
        self.create_subscription(Twist, "/cmd_vel_to_robot", self._cb_robot, 10)
        print("")
        print("--- cmd_vel 흐름 비교 ---")
        print("  /cmd_vel_nav     : Nav2 출력")
        print("  /cmd_vel         : 최종 ROS cmd_vel")
        print("  /cmd_vel_to_robot: 로봇 좌표계 변환 후")
        print("")

    def _print_snapshot(self, source):
        nav = self.latest["/cmd_vel_nav"]
        cmd = self.latest["/cmd_vel"]
        robot = self.latest["/cmd_vel_to_robot"]
        print(f"[update: {source}]")
        print("  /cmd_vel_nav      ", fmt_twist(nav) if nav else "(no message yet)")
        print("  /cmd_vel          ", fmt_twist(cmd) if cmd else "(no message yet)")
        print("  /cmd_vel_to_robot ", fmt_twist(robot) if robot else "(no message yet)")
        print("")

    def _cb_nav(self, msg):
        self.latest["/cmd_vel_nav"] = msg
        self._print_snapshot("/cmd_vel_nav")

    def _cb_cmd(self, msg):
        self.latest["/cmd_vel"] = msg
        self._print_snapshot("/cmd_vel")

    def _cb_robot(self, msg):
        self.latest["/cmd_vel_to_robot"] = msg
        self._print_snapshot("/cmd_vel_to_robot")


def main():
    rclpy.init()
    node = CmdVelMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
PY
