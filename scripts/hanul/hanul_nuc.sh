#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SESSION="hanul"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "기존 tmux 세션 '$SESSION'에 붙습니다."
  exec tmux attach -t "$SESSION"
fi

MOTOR_PORT="${MOTOR_PORT:-/dev/ttyUSB1}"
LIDAR_PORT="${LIDAR_PORT:-/dev/ttyUSB0}"

tmux new-session -d -s "$SESSION" -n nuc
tmux send-keys -t "${SESSION}:0.0" "cd $PROJECT_ROOT && source /opt/ros/jazzy/setup.bash && export PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH && export MOTOR_PORT=$MOTOR_PORT && cd controllers/hanul_controller_nuc && python3 hanul_controller_nuc.py" C-m
tmux split-window -h -t "${SESSION}:0.0"
tmux send-keys -t "${SESSION}:0.1" "source /opt/ros/jazzy/setup.bash && [ -f ~/ros2_ws/install/setup.bash ] && source ~/ros2_ws/install/setup.bash ; LIDAR_PORT=\${LIDAR_PORT:-/dev/ttyUSB0} && [ -e \"\$LIDAR_PORT\" ] && sudo chmod 666 \"\$LIDAR_PORT\" ; ros2 launch sllidar_ros2 sllidar_a1_launch.py serial_port:=${LIDAR_PORT}" C-m
tmux select-layout -t "${SESSION}:0" even-horizontal
exec tmux attach -t "$SESSION"
