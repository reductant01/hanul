#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SESSION="hanul"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "기존 tmux 세션 '$SESSION'에 붙습니다."
  exec tmux attach -t "$SESSION"
fi

tmux new-session -d -s "$SESSION" -n nuc
tmux send-keys -t "${SESSION}:0.0" "cd $PROJECT_ROOT && source /opt/ros/jazzy/setup.bash && export PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH && cd controllers/hanul_controller_nuc && python3 hanul_controller_nuc.py" C-m
tmux split-window -h -t "${SESSION}:0.0"
tmux send-keys -t "${SESSION}:0.1" "source /opt/ros/jazzy/setup.bash && echo 'A1 라이다: 여기서 드라이버 실행 (예: ros2 run ... /scan 발행)' && exec bash" C-m
tmux select-layout -t "${SESSION}:0" even-horizontal
exec tmux attach -t "$SESSION"
