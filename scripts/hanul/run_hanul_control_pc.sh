#!/bin/bash
# 제어 PC에서만 실행. SLAM 또는 Map/AMCL/Nav2, RViz, Teleop. NUC에서는 run_hanul_nuc.sh 별도 실행.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$PROJECT_ROOT/scripts/hanul/hanul_terminator.sh"

MODE_INPUT="${1:-loc}"
case "$MODE_INPUT" in
  map|mapping)   MODE="control_pc_map" ;;
  loc|localization) MODE="control_pc_loc" ;;
  *)
    echo "사용법: $0 [map|loc]"
    echo "  map: SLAM + RViz + Teleop (NUC에서 run_hanul_nuc.sh 별도 실행)"
    echo "  loc: Map Server + AMCL + Nav2 + RViz + Teleop (NUC에서 run_hanul_nuc.sh 별도 실행)"
    echo "  NUC와 같은 네트워크, 같은 ROS_DOMAIN_ID 필요."
    exit 1
    ;;
esac

TITLE_TOP_1="[NUC] run_hanul_nuc.sh 별도 실행"
CMD_TOP_1="$CMD_EMPTY"

if [[ "$MODE" == "control_pc_map" ]]; then
  TITLE_TOP_2="SLAM Toolbox"
  TITLE_TOP_3="Robot Model"
  TITLE_TOP_4="Empty"
  TITLE_BOTTOM_3="Collision Monitor"
  TITLE_BOTTOM_4="cmd_vel_output"

  CMD_TOP_2="$SETUP_CMD; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false slam_params_file:=$PROJECT_ROOT/config/hanul/slam_toolbox_params.yaml; exec bash"
  CMD_TOP_3="$CMD_ROBOT_MODEL"
  CMD_TOP_4="$CMD_EMPTY"
  CMD_BOTTOM_3="$CMD_COLLISION_MONITOR"
  CMD_BOTTOM_4="$CMD_VEL_OUTPUT"
  CMD_RVIZ="$CMD_RVIZ_MAP"
elif [[ "$MODE" == "control_pc_loc" ]]; then
  TITLE_TOP_2="Robot Model"
  TITLE_TOP_3="Empty"
  TITLE_TOP_4="cmd_vel_output"
  TITLE_BOTTOM_3="Localization"
  TITLE_BOTTOM_4="Nav2"
  
  CMD_TOP_2="$CMD_ROBOT_MODEL"
  CMD_TOP_3="$CMD_EMPTY"
  CMD_TOP_4="$CMD_VEL_OUTPUT"
  CMD_BOTTOM_3="$SETUP_CMD; cd $PROJECT_ROOT && ros2 launch nav2_bringup localization_launch.py map:=$MAP_YAML params_file:=$PROJECT_ROOT/config/hanul/amcl_params.yaml use_sim_time:=False autostart:=True; exec bash"
  CMD_BOTTOM_4="$SETUP_CMD; cd $PROJECT_ROOT && python3 scripts/wait_lifecycle_active.py /map_server 20; python3 scripts/wait_lifecycle_active.py /amcl 20; (ros2 launch nav2_bringup navigation_launch.py params_file:=$PROJECT_ROOT/config/hanul/nav2_params.yaml use_sim_time:=False autostart:=True &); python3 scripts/wait_nav2_active.py 30; exec bash"
  CMD_RVIZ="$CMD_RVIZ_LOC"
fi

run_terminator
