#!/usr/bin/env bash
# /cmd_vel(ROS)와 /cmd_vel_to_robot(로봇 입력) 동시에 echo.
# Ctrl+C 종료.
set -e
source /opt/ros/jazzy/setup.bash

echo ""
echo "실행할 명령:"
echo "  ros2 topic echo /cmd_vel"
echo "  ros2 topic echo /cmd_vel_to_robot"
echo ""
echo "--- 출력 (위: /cmd_vel, 아래: /cmd_vel_to_robot) ---"
echo ""

ros2 topic echo /cmd_vel &
PID=$!
trap 'kill $PID 2>/dev/null' EXIT
ros2 topic echo /cmd_vel_to_robot
