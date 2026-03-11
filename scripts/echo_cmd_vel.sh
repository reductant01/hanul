#!/usr/bin/env bash
# /cmd_vel(ROS)와 /cmd_vel_to_robot(로봇 입력) 동시에 echo.
# Ctrl+C 종료.
# 사용: source /opt/ros/jazzy/setup.bash && ./scripts/echo_cmd_vel.sh
set -e
source /opt/ros/jazzy/setup.bash
echo "  ROS   /cmd_vel (위)  |  Robot /cmd_vel_to_robot (아래)"
echo "---"
ros2 topic echo /cmd_vel &
PID=$!
trap 'kill $PID 2>/dev/null' EXIT
ros2 topic echo /cmd_vel_to_robot
