"""
ROS /cmd_vel Twist를 로봇 좌표계 Twist로 변환.
"""
from geometry_msgs.msg import Twist


ROS_TO_ROBOT_VX_SIGN = 1.0
ROS_TO_ROBOT_VY_SIGN = -1.0
ROS_TO_ROBOT_W_SIGN = 1.0


class CmdVelConverter:
    """ROS /cmd_vel Twist를 로봇 좌표계 Twist로 변환."""

    @staticmethod
    def to_robot_twist(msg):
        vx = ROS_TO_ROBOT_VX_SIGN * msg.linear.x
        vy = ROS_TO_ROBOT_VY_SIGN * msg.linear.y
        w = ROS_TO_ROBOT_W_SIGN * msg.angular.z
        out = Twist()
        out.linear.x = float(vx)
        out.linear.y = float(vy)
        out.linear.z = 0.0
        out.angular.x = 0.0
        out.angular.y = 0.0
        out.angular.z = float(w)
        return (vx, vy, w), out
