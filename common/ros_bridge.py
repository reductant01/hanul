"""
ROS 2 브릿지 모듈. 메시지 생성/로드는 common 내 다른 모듈에서 하고, 여기서는 발행만.
"""
import threading

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist, PolygonStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState, LaserScan
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster

from common.collision_polygons import (
    create_approach_polygon_stamped,
    create_stop_polygon_stamped,
    create_slowdown_polygon_stamped,
)
from common.cmd_vel_converter import CmdVelConverter


class RobotROSBridge(Node):
    """ROS 2 토픽 통신 담당"""

    def __init__(self, node_name='robot_controller_node', enable_scan_publisher=True, enable_polygon_publishers=True):
        super().__init__(node_name)

        self.create_subscription(Twist, '/cmd_vel', self._on_cmd_vel_received, 10)
        self.cmd_vel_to_robot_pub = self.create_publisher(Twist, '/cmd_vel_to_robot', 10)
        self.scan_raw_publisher = self.create_publisher(LaserScan, '/scan_raw', qos_profile_sensor_data)
        self.scan_publisher = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data) if enable_scan_publisher else None
        self.odom_publisher = self.create_publisher(Odometry, '/odom', 10)
        self.joint_state_publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.polygon_approach_pub = self.create_publisher(PolygonStamped, '/polygon_approach', 10) if enable_polygon_publishers else None
        self.polygon_stop_pub = self.create_publisher(PolygonStamped, '/polygon_stop', 10) if enable_polygon_publishers else None
        self.polygon_slowdown_pub = self.create_publisher(PolygonStamped, '/polygon_slowdown', 10) if enable_polygon_publishers else None

        self.cmd_vel = [0.0, 0.0, 0.0]
        self.cmd_vel_lock = threading.Lock()
        self._last_scan = None
        self._scan_lock = threading.Lock()

    def _on_cmd_vel_received(self, msg):
        (vx, vy, w), robot_twist = CmdVelConverter.to_robot_twist(msg)
        with self.cmd_vel_lock:
            self.cmd_vel = [vx, vy, w]
        self.cmd_vel_to_robot_pub.publish(robot_twist)

    def get_cmd_vel(self):
        with self.cmd_vel_lock:
            return (self.cmd_vel[0], self.cmd_vel[1], self.cmd_vel[2])

    def publish_scan(self, scan_msg):
        if scan_msg and self.scan_publisher is not None:
            with self._scan_lock:
                self._last_scan = scan_msg
            self.scan_publisher.publish(scan_msg)

    def publish_scan_raw(self, scan_msg):
        if scan_msg:
            self.scan_raw_publisher.publish(scan_msg)

    def publish_odom(self, odom_msg):
        if odom_msg:
            self.odom_publisher.publish(odom_msg)

    def publish_joint_states(self, joint_state_msg):
        if joint_state_msg:
            self.joint_state_publisher.publish(joint_state_msg)

    def publish_transform(self, transform_msg):
        if transform_msg:
            self.tf_broadcaster.sendTransform(transform_msg)

    def publish_static_transform(self, transform_msg):
        if transform_msg:
            self.static_tf_broadcaster.sendTransform(transform_msg)

    def publish_collision_polygons_rviz(self, stamp=None):
        if self.polygon_approach_pub is None or self.polygon_stop_pub is None or self.polygon_slowdown_pub is None:
            return
        if stamp is None:
            stamp = self.get_clock().now().to_msg()
        frame_id = 'base_link'
        self.polygon_approach_pub.publish(create_approach_polygon_stamped(frame_id, stamp))
        self.polygon_stop_pub.publish(create_stop_polygon_stamped(frame_id, stamp))
        self.polygon_slowdown_pub.publish(create_slowdown_polygon_stamped(frame_id, stamp))


def init_ros_node():
    if not rclpy.ok():
        rclpy.init(args=None)


def shutdown_ros_node():
    if rclpy.ok():
        rclpy.shutdown()
