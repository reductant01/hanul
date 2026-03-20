"""
odom 메시지 생성. 발행은 ros_bridge.
"""
import math
from nav_msgs.msg import Odometry


def create_odometry_message(
    x,
    y,
    theta,
    ros_node,
    stamp=None,
    frame_id="odom",
    child_frame_id="base_footprint",
    linear_x=0.0,
    linear_y=0.0,
    angular_z=0.0,
):
    msg = Odometry()
    msg.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
    msg.header.frame_id = frame_id
    msg.child_frame_id = child_frame_id
    msg.pose.pose.position.x = float(x)
    msg.pose.pose.position.y = float(y)
    msg.pose.pose.position.z = 0.0
    msg.pose.pose.orientation.x = 0.0
    msg.pose.pose.orientation.y = 0.0
    msg.pose.pose.orientation.z = math.sin(theta / 2.0)
    msg.pose.pose.orientation.w = math.cos(theta / 2.0)
    msg.twist.twist.linear.x = float(linear_x)
    msg.twist.twist.linear.y = float(linear_y)
    msg.twist.twist.linear.z = 0.0
    msg.twist.twist.angular.x = 0.0
    msg.twist.twist.angular.y = 0.0
    msg.twist.twist.angular.z = float(angular_z)
    return msg
