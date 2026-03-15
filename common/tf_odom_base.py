"""
odom → base_footprint TF 생성. 발행은 ros_bridge.
"""
import math
from geometry_msgs.msg import TransformStamped


def create_odometry_transform(x, y, theta, ros_node, stamp=None, yaw_offset=0.0):
    t = TransformStamped()
    t.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
    t.header.frame_id = 'odom'
    t.child_frame_id = 'base_footprint'
    t.transform.translation.x = x
    t.transform.translation.y = y
    t.transform.translation.z = 0.0
    yaw = theta + yaw_offset
    t.transform.rotation.x = 0.0
    t.transform.rotation.y = 0.0
    t.transform.rotation.z = math.sin(yaw / 2.0)
    t.transform.rotation.w = math.cos(yaw / 2.0)
    return t
