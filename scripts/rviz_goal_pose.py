#!/usr/bin/env python3
"""
Nav2 NavigateToPose 목표 전송. RViz Nav2 Goal을 코드로 대신.
맵 원점 (0, 0, 0) 또는 지정 (x, y, yaw)로 이동. loc 모드에서 Nav2가 떠 있는 상태에서 실행.

중요: 초기 위치(Initial Pose)를 맵 원점 (0,0,0)으로 두고 이 스크립트를 돌리면,
      경로 길이가 0이라 "목표 도착"으로 바로 끝나고 로봇이 움직이지 않습니다.
      반드시 RViz "2D Pose Estimate"로 로봇이 실제 있는 위치를 찍은 뒤
      이 스크립트를 실행하세요.

사용법:
  source /opt/ros/jazzy/setup.bash
  python3 scripts/rviz_goal_pose.py
  python3 scripts/rviz_goal_pose.py 1.0 0.5   # (1, 0.5) 로 이동
"""
import sys

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.action import ActionClient
    from nav2_msgs.action import NavigateToPose
    from geometry_msgs.msg import PoseStamped
except ImportError as e:
    print("ROS 2 환경을 먼저 로드하세요: source /opt/ros/jazzy/setup.bash")
    sys.exit(1)


class RvizGoalPose(Node):
    def __init__(self):
        super().__init__("rviz_goal_pose")
        self._client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self._done = False
        self._succeeded = False

    def send_goal(self, x=0.0, y=0.0, yaw=0.0):
        import math
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.get_logger().info("navigate_to_pose 서버 대기 중...")
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("서버 없음. Nav2(loc)가 실행 중인지 확인하세요.")
            return False

        if x == 0.0 and y == 0.0:
            self.get_logger().info(
                "맵 원점 (0, 0)으로 목표 전송. "
                "초기 위치가 이미 (0,0)이면 경로가 없어 움직이지 않습니다. "
                "2D Pose Estimate로 로봇 실제 위치를 먼저 설정하세요."
            )
        self.get_logger().info("목표 (%.2f, %.2f) 로 전송." % (x, y))
        send_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_cb,
        )
        rclpy.spin_until_future_complete(self, send_future)
        if not send_future.result().accepted:
            self.get_logger().error("목표 거부됨.")
            return False

        result_future = send_future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()
        self._succeeded = result is not None and result.result is not None
        if self._succeeded:
            self.get_logger().info("목표 도착 완료.")
        else:
            self.get_logger().warn("목표 미도착 또는 오류.")
        return self._succeeded

    def _feedback_cb(self, fb):
        pass


def main():
    rclpy.init()
    node = RvizGoalPose()
    x = 0.0
    y = 0.0
    yaw = 0.0
    if len(sys.argv) >= 3:
        try:
            x = float(sys.argv[1])
            y = float(sys.argv[2])
            if len(sys.argv) >= 4:
                yaw = float(sys.argv[3])
        except ValueError:
            pass
    ok = node.send_goal(x=x, y=y, yaw=yaw)
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
