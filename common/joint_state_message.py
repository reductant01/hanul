"""
JointState 메시지 생성. 발행은 ros_bridge.
"""
from sensor_msgs.msg import JointState


def create_joint_state_message(
    ros_node,
    stamp=None,
    names=None,
    positions=None,
    velocities=None,
    efforts=None,
):
    msg = JointState()
    msg.header.stamp = stamp if stamp is not None else ros_node.get_clock().now().to_msg()
    msg.name = list(names or [])
    msg.position = list(positions or [])
    msg.velocity = list(velocities or [])
    msg.effort = list(efforts or [])
    return msg
