#!/usr/bin/env bash
# 한울 관련으로 남은 Webots/RViz/ROS 프로세스 정리. DDS SHM 잠금 파일 일부 삭제.
# 사용: source "$PROJECT_ROOT/scripts/hanul/kill_hanul_process.sh" 후 hanul_cleanup_previous_sessions
#       또는: bash scripts/hanul/kill_hanul_process.sh

hanul_cleanup_previous_sessions() {
  pkill -x webots 2>/dev/null || true
  pkill -x Webots 2>/dev/null || true
  pkill -f '[r]viz2' 2>/dev/null || true
  pkill -f 'hanul_controller_webots' 2>/dev/null || true
  pkill -f 'controllers/hanul_controller/hanul_controller.py' 2>/dev/null || true
  pkill -f '[l]idar_scan_mask.py' 2>/dev/null || true
  pkill -f '[c]md_vel_output' 2>/dev/null || true
  pkill -f '[c]md_vel_input.py' 2>/dev/null || true
  pkill -f '[o]nline_async_launch.py' 2>/dev/null || true
  pkill -f '[n]avigation_launch.py' 2>/dev/null || true
  pkill -f '[l]ocalization_launch.py' 2>/dev/null || true
  pkill -f 'hanul_robot_state_publisher_params.yaml' 2>/dev/null || true
  sleep 1
  rm -f /dev/shm/fastrtps_port* /dev/shm/fastdds_shm* 2>/dev/null || true
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  hanul_cleanup_previous_sessions
fi
