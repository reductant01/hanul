"""
ROS 2 브릿지 모듈
ROS 2 토픽 구독/발행만 담당합니다.

책임:
✅ /cmd_vel 토픽 구독 (명령 받기)
✅ /scan 토픽 발행 (라이다 데이터)
✅ /tf 토픽 발행 (좌표 변환)
❌ 계산 (계산은 다른 모듈에서)
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster
import threading


class HanulROSBridge(Node):
    """ROS 2 토픽 통신 담당"""
    
    def __init__(self):
        super().__init__('hanul_controller_node')
        
        # /cmd_vel 구독 (teleop_twist_keyboard에서 오는 명령)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # /scan 발행 (라이다 데이터)
        self.scan_publisher = self.create_publisher(LaserScan, '/scan', 10)
        
        # /tf 발행 (좌표 변환)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.static_tf_broadcaster = StaticTransformBroadcaster(self)
        
        # 현재 명령 (스레드 안전)
        self.cmd_vel = [0.0, 0.0, 0.0]  # vx, vy, w
        self.cmd_vel_lock = threading.Lock()
        self.cmd_vel_scale = 30.0
        self.cmd_vel_scale_thresh_linear = 0.05
        self.cmd_vel_scale_thresh_angular = 0.02
        self.cmd_vel_max = (0.5, 0.5, 1.9)
        self.cmd_vel_min = (-0.35, -0.5, -1.9)
    
    def cmd_vel_callback(self, msg):
        vx = msg.linear.x
        vy = -msg.linear.y
        w = msg.angular.z
        if (abs(vx) < self.cmd_vel_scale_thresh_linear
                and abs(vy) < self.cmd_vel_scale_thresh_linear
                and abs(w) < self.cmd_vel_scale_thresh_angular
                and (vx != 0 or vy != 0 or w != 0)):
            vx = max(self.cmd_vel_min[0], min(self.cmd_vel_max[0], vx * self.cmd_vel_scale))
            vy = max(self.cmd_vel_min[1], min(self.cmd_vel_max[1], vy * self.cmd_vel_scale))
            w = max(self.cmd_vel_min[2], min(self.cmd_vel_max[2], w * self.cmd_vel_scale))
        with self.cmd_vel_lock:
            self.cmd_vel = [vx, vy, w]
    
    def get_cmd_vel(self):
        """현재 속도 명령 반환 (스레드 안전)"""
        with self.cmd_vel_lock:
            return self.cmd_vel[:]
    
    def publish_scan(self, scan_msg):
        """라이다 스캔 데이터 발행
        
        Args:
            scan_msg: LaserScan 메시지 (이미 생성된 것)
        """
        if scan_msg:
            self.scan_publisher.publish(scan_msg)
    
    def publish_transform(self, transform_msg):
        """좌표 변환 발행
        
        Args:
            transform_msg: TransformStamped 메시지 (이미 생성된 것)
        """
        if transform_msg:
            self.tf_broadcaster.sendTransform(transform_msg)

    def publish_static_transform(self, transform_msg):
        """정적 좌표 변환 발행 (/tf_static)"""
        if transform_msg:
            self.static_tf_broadcaster.sendTransform(transform_msg)


def init_ros_node():
    """ROS 2 노드 초기화"""
    if not rclpy.ok():
        rclpy.init(args=None)


def shutdown_ros_node():
    """ROS 2 노드 종료"""
    if rclpy.ok():
        rclpy.shutdown()
