"""
ROS 2 브릿지 모듈
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster
import threading


class RobotROSBridge(Node):
    """ROS 2 토픽 통신 담당"""

    def __init__(self, node_name='robot_controller_node'):
        super().__init__(node_name)

        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.scan_publisher = self.create_publisher(LaserScan, '/scan', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)

        self.cmd_vel = [0.0, 0.0, 0.0]
        self.cmd_vel_lock = threading.Lock()
        self.cmd_vel_scale = 30.0
        self.cmd_vel_scale_thresh_linear = 0.01
        self.cmd_vel_scale_thresh_angular = 0.01

    def cmd_vel_callback(self, msg):
        vx = -msg.linear.x
        vy = msg.linear.y
        w = -msg.angular.z
        if (abs(vx) < self.cmd_vel_scale_thresh_linear
                and abs(vy) < self.cmd_vel_scale_thresh_linear
                and abs(w) < self.cmd_vel_scale_thresh_angular
                and (vx != 0 or vy != 0 or w != 0)):
            vx *= self.cmd_vel_scale
            vy *= self.cmd_vel_scale
            w *= self.cmd_vel_scale
        with self.cmd_vel_lock:
            self.cmd_vel = [vx, vy, w]

    def get_cmd_vel(self):
        with self.cmd_vel_lock:
            return self.cmd_vel[:]

    def publish_scan(self, scan_msg):
        if scan_msg:
            self.scan_publisher.publish(scan_msg)

    def publish_transform(self, transform_msg):
        if transform_msg:
            self.tf_broadcaster.sendTransform(transform_msg)

    def publish_static_transform(self, transform_msg):
        if transform_msg:
            self.static_tf_broadcaster.sendTransform(transform_msg)


def init_ros_node():
    if not rclpy.ok():
        rclpy.init(args=None)


def shutdown_ros_node():
    if rclpy.ok():
        rclpy.shutdown()
