"""
base_footprint → lidar_link / laser TF 생성. 발행은 ros_bridge.
"""
import math
from geometry_msgs.msg import TransformStamped


class TFBaseLidar:
    def __init__(self, lidar_x=0.085, lidar_y=0.0, lidar_z=0.113):
        self.lidar_x = lidar_x
        self.lidar_y = lidar_y
        self.lidar_z = lidar_z

    def create_lidar_transform(self, ros_node, stamp=None, lidar_yaw=0.0):
        t = TransformStamped()
        t.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
        t.header.frame_id = 'base_footprint'
        t.child_frame_id = 'lidar_link'
        t.transform.translation.x = self.lidar_x
        t.transform.translation.y = self.lidar_y
        t.transform.translation.z = self.lidar_z
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(lidar_yaw / 2.0)
        t.transform.rotation.w = math.cos(lidar_yaw / 2.0)
        return t

    def create_laser_transform(self, ros_node, stamp=None, lidar_yaw=0.0):
        t = self.create_lidar_transform(ros_node, stamp=stamp, lidar_yaw=lidar_yaw)
        t.child_frame_id = 'laser'
        return t
