"""
map→odom identity 판단 및 TF 생성. 발행은 ros_bridge.publish_transform.
"""
import os

from geometry_msgs.msg import TransformStamped


def should_publish_map_odom_identity(x, y, theta, threshold=0.1):
    # map->odom 은 원칙적으로 SLAM Toolbox 또는 AMCL 이 담당한다.
    # 기본값은 비활성으로 두고, 정말 필요할 때만 환경변수로 켠다.
    enabled = os.getenv("HANUL_PUBLISH_MAP_ODOM_IDENTITY", "").lower() in ("1", "true", "yes", "on")
    if not enabled:
        return False
    if abs(x) < threshold and abs(y) < threshold and abs(theta) < threshold:
        return True
    return False


def create_map_odom_identity(ros_node, stamp=None):
    t = TransformStamped()
    t.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
    t.header.frame_id = 'map'
    t.child_frame_id = 'odom'
    t.transform.translation.x = 0.0
    t.transform.translation.y = 0.0
    t.transform.translation.z = 0.0
    t.transform.rotation.x = 0.0
    t.transform.rotation.y = 0.0
    t.transform.rotation.z = 0.0
    t.transform.rotation.w = 1.0
    return t
