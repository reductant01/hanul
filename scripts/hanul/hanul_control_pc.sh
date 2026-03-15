#!/bin/bash
# 제어 PC에서만 실행. SLAM 또는 Map/AMCL/Nav2, RViz, Teleop. NUC에서는 hanul_nuc.sh 별도 실행.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$PROJECT_ROOT/scripts/hanul/hanul_terminator.sh"

MODE_INPUT="${1:-loc}"
case "$MODE_INPUT" in
  map|mapping)   MODE="control_pc_map" ;;
  loc|localization) MODE="control_pc_loc" ;;
  *)
    echo "사용법: $0 [map|loc]"
    echo "  map: SLAM + RViz + Teleop (NUC에서 hanul_nuc.sh 별도 실행)"
    echo "  loc: Map Server + AMCL + Nav2 + RViz + Teleop (NUC에서 hanul_nuc.sh 별도 실행)"
    echo "  NUC와 같은 네트워크, 같은 ROS_DOMAIN_ID 필요."
    exit 1
    ;;
esac

TITLE_TOP_1="[NUC] hanul_nuc.sh 별도 실행"
CMD_TOP_1="$CMD_EMPTY"

if [[ "$MODE" == "control_pc_map" ]]; then
  TITLE_TOP_2="SLAM Toolbox"
  TITLE_TOP_3="Empty"
  TITLE_TOP_4="Empty"
  TITLE_BOTTOM_3="Collision Monitor"
  TITLE_BOTTOM_4="cmd_vel_output"

  CMD_TOP_2="$SETUP_CMD; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false slam_params_file:=$PROJECT_ROOT/config/hanul/slam_toolbox_params.yaml; exec bash"
  CMD_TOP_3="$CMD_EMPTY"
  CMD_TOP_4="$CMD_EMPTY"
  CMD_BOTTOM_3="$CMD_COLLISION_MONITOR"
  CMD_BOTTOM_4="$CMD_VEL_OUTPUT"
  CMD_RVIZ="$CMD_RVIZ_MAP"
elif [[ "$MODE" == "control_pc_loc" ]]; then
  TITLE_TOP_2="Map Server"
  TITLE_TOP_3="AMCL"
  TITLE_TOP_4="cmd_vel_output"
  TITLE_BOTTOM_3="Init Pose"
  TITLE_BOTTOM_4="Nav2"
  
  CMD_TOP_2="$SETUP_CMD; (ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=$MAP_YAML &); sleep 2; ros2 lifecycle set /map_server configure 2>/dev/null; ros2 lifecycle set /map_server activate 2>/dev/null; exec bash"
  CMD_TOP_3="$SETUP_CMD; sleep 4; (ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=false --params-file $PROJECT_ROOT/config/hanul/amcl_params.yaml &); sleep 2; ros2 lifecycle set /amcl configure 2>/dev/null; ros2 lifecycle set /amcl activate 2>/dev/null; exec bash"
  CMD_TOP_4="sleep 6; $CMD_VEL_OUTPUT"
  CMD_BOTTOM_3="$SETUP_CMD; sleep 3; cd $PROJECT_ROOT && python3 scripts/rviz_initial_pose.py; exec bash"
  CMD_BOTTOM_4="$SETUP_CMD; (ros2 launch nav2_bringup navigation_launch.py params_file:=$PROJECT_ROOT/config/hanul/nav2_params.yaml use_sim_time:=False autostart:=True &); sleep 8; exec bash"
  CMD_RVIZ="$CMD_RVIZ_LOC"
fi

run_terminator
