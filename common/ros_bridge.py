"""
ROS 2 브릿지 모듈
"""
import ast
import math
import os
import threading

import rclpy
import yaml
from rclpy.node import Node
from geometry_msgs.msg import Twist, PolygonStamped, Point32
from sensor_msgs.msg import LaserScan
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster


def _load_collision_polygons_from_nav2_params():
    project_root = os.environ.get('PROJECT_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_root, 'config', 'hanul', 'nav2_params.yaml')
    default_stop = [(0.3, 0.3), (0.3, -0.3), (0, -0.3), (0, 0.3)]
    default_slowdown = [(0.6, 0.6), (0.6, -0.6), (-0.6, -0.6), (-0.6, 0.6)]
    if not os.path.isfile(path):
        return default_stop, default_slowdown
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        params = (data or {}).get('collision_monitor', {}).get('ros__parameters') or {}
        stop_raw = params.get('PolygonStop', {}).get('points')
        slow_raw = params.get('PolygonSlow', {}).get('points')
        stop = [tuple(p) for p in ast.literal_eval(stop_raw)] if isinstance(stop_raw, str) else default_stop
        slow = [tuple(p) for p in ast.literal_eval(slow_raw)] if isinstance(slow_raw, str) else default_slowdown
        return stop if len(stop) >= 3 else default_stop, slow if len(slow) >= 3 else default_slowdown
    except Exception:
        return default_stop, default_slowdown


def _make_polygon_stamped(frame_id, stamp, points_xy):
    msg = PolygonStamped()
    msg.header.frame_id = frame_id
    msg.header.stamp = stamp
    for x, y in points_xy:
        p = Point32()
        p.x = float(x)
        p.y = float(y)
        p.z = 0.0
        msg.polygon.points.append(p)
    return msg


class RobotROSBridge(Node):
    """ROS 2 토픽 통신 담당"""

    def __init__(self, node_name='robot_controller_node'):
        super().__init__(node_name)

        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.cmd_vel_to_robot_pub = self.create_publisher(Twist, '/cmd_vel_to_robot', 10)
        self.scan_publisher = self.create_publisher(LaserScan, '/scan', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        self.polygon_approach_pub = self.create_publisher(PolygonStamped, '/polygon_approach', 10)
        self.polygon_stop_pub = self.create_publisher(PolygonStamped, '/polygon_stop', 10)
        self.polygon_slowdown_pub = self.create_publisher(PolygonStamped, '/polygon_slowdown', 10)

        self.cmd_vel = [0.0, 0.0, 0.0]
        self.cmd_vel_lock = threading.Lock()
        self._last_scan = None
        self._scan_lock = threading.Lock()

        n = 24
        r_approach = 0.17
        self._approach_points = [(r_approach * math.cos(2 * math.pi * i / n), r_approach * math.sin(2 * math.pi * i / n)) for i in range(n)]
        self._stop_points, self._slowdown_points = _load_collision_polygons_from_nav2_params()

    def cmd_vel_callback(self, msg):
        vx = -msg.linear.x
        vy = msg.linear.y
        w = -msg.angular.z
        with self.cmd_vel_lock:
            self.cmd_vel = [vx, vy, w]
        out = Twist()
        out.linear.x = float(vx)
        out.linear.y = float(vy)
        out.linear.z = 0.0
        out.angular.x = 0.0
        out.angular.y = 0.0
        out.angular.z = float(w)
        self.cmd_vel_to_robot_pub.publish(out)

    def get_cmd_vel(self):
        with self.cmd_vel_lock:
            return (self.cmd_vel[0], self.cmd_vel[1], self.cmd_vel[2])

    def publish_scan(self, scan_msg):
        if scan_msg:
            with self._scan_lock:
                self._last_scan = scan_msg
            self.scan_publisher.publish(scan_msg)

    def publish_transform(self, transform_msg):
        if transform_msg:
            self.tf_broadcaster.sendTransform(transform_msg)

    def publish_static_transform(self, transform_msg):
        if transform_msg:
            self.static_tf_broadcaster.sendTransform(transform_msg)

    def publish_collision_polygons_rviz(self, stamp=None):
        if stamp is None:
            stamp = self.get_clock().now().to_msg()
        frame_id = 'base_footprint'
        self.polygon_approach_pub.publish(_make_polygon_stamped(frame_id, stamp, self._approach_points))
        self.polygon_stop_pub.publish(_make_polygon_stamped(frame_id, stamp, self._stop_points))
        self.polygon_slowdown_pub.publish(_make_polygon_stamped(frame_id, stamp, self._slowdown_points))


def init_ros_node():
    if not rclpy.ok():
        rclpy.init(args=None)


def shutdown_ros_node():
    if rclpy.ok():
        rclpy.shutdown()
