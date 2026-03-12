"""
map→odom identity TF 발행 여부 및 생성.
스캔 시각에 map→odom이 없어 RViz/AMCL이 드롭하는 것을 완화하기 위해,
로봇이 원점 근처일 때만 map=odom identity를 스캔과 같은 stamp로 발행.
Webots·NUC 컨트롤러 공통 사용.
"""
from geometry_msgs.msg import TransformStamped


def should_publish_map_odom_identity(x, y, theta, threshold=0.1):
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
