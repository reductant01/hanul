#!/usr/bin/env bash
# odom → base_footprint TF 한 줄씩 출력 (ros2 topic echo와 유사).
# Ctrl+C 종료.
# 사용: source /opt/ros/jazzy/setup.bash && ./scripts/echo_odom_pose.sh
set -e
source /opt/ros/jazzy/setup.bash
ros2 run tf2_ros tf2_echo odom base_footprint
