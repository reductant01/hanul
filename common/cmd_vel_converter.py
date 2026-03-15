"""
ROS /cmd_vel Twist를 로봇 좌표계 Twist로 변환.
"""
from geometry_msgs.msg import Twist


class CmdVelConverter:
    """ROS /cmd_vel Twist를 로봇 좌표계 Twist로 변환."""

    @staticmethod
    def to_robot_twist(msg):
        vx = -msg.linear.x
        vy = msg.linear.y
        w = -msg.angular.z
        out = Twist()
        out.linear.x = float(vx)
        out.linear.y = float(vy)
        out.linear.z = 0.0
        out.angular.x = 0.0
        out.angular.y = 0.0
        out.angular.z = float(w)
        return (vx, vy, w), out
