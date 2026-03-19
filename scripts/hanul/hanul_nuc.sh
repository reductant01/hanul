#!/bin/bash
# NUC에서만 실행. 컨트롤러(다이나믹셀) + 라이다(S2). 제어 PC에서는 hanul_control_pc.sh 실행.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SESSION="hanul"

DEV_WHEEL=wheel
DEV_LIDAR=lidar
MOTOR_PORT="${MOTOR_PORT:-/dev/${DEV_WHEEL}}"
LIDAR_PORT="${LIDAR_PORT:-/dev/${DEV_LIDAR}}"
# 다이나믹셀이 USB1(ttyUSB1)에 연결된 경우 udev 미사용 시: MOTOR_PORT=/dev/ttyUSB1 로 실행

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "기존 tmux 세션 '$SESSION'에 붙습니다."
  exec tmux attach -t "$SESSION"
fi

tmux new-session -d -s "$SESSION" -n nuc
tmux send-keys -t "${SESSION}:0.0" "cd $PROJECT_ROOT && source /opt/ros/jazzy/setup.bash && export PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH && export MOTOR_PORT=$MOTOR_PORT && [ -e \"$MOTOR_PORT\" ] && sudo chmod 666 \"$MOTOR_PORT\" ; cd controllers/hanul_controller_nuc && python3 hanul_controller_nuc.py" C-m
tmux split-window -h -t "${SESSION}:0.0"
tmux send-keys -t "${SESSION}:0.1" "cd $PROJECT_ROOT && source /opt/ros/jazzy/setup.bash && [ -f ~/ros2_ws/install/setup.bash ] && source ~/ros2_ws/install/setup.bash ; export PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH ; LIDAR_PORT=$LIDAR_PORT && [ -e \"\$LIDAR_PORT\" ] && sudo chmod 666 \"\$LIDAR_PORT\" ; ros2 run sllidar_ros2 sllidar_node --ros-args -p channel_type:=serial -p serial_port:=\$LIDAR_PORT -p serial_baudrate:=1000000 -p frame_id:=laser -p inverted:=false -p angle_compensate:=true -p scan_mode:=DenseBoost -r scan:=/scan_raw & python3 common/lidar_scan_mask.py --ros-args --params-file $PROJECT_ROOT/config/hanul/laser_rear_mask.yaml" C-m
tmux select-layout -t "${SESSION}:0" even-horizontal
exec tmux attach -t "$SESSION"
