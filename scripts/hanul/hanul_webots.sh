#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$PROJECT_ROOT/scripts/hanul/hanul_terminator.sh"

MODE_INPUT="${1:-loc}"
case "$MODE_INPUT" in
  map|mapping)   MODE="map" ;;
  loc|localization) MODE="loc" ;;
  *)
    echo "사용법: $0 [map|loc]"
    exit 1
    ;;
esac

if [[ "$MODE" == "map" ]]; then
  TITLE_TOP_1="Webots"
  TITLE_TOP_2="SLAM Toolbox"
  TITLE_TOP_3="Lidar Mask"
  TITLE_TOP_4="Robot Model"
  TITLE_BOTTOM_3="Collision Monitor"
  TITLE_BOTTOM_4="cmd_vel_output"

  CMD_TOP_1="$CMD_WEBOTS"
  CMD_TOP_2="$SETUP_CMD; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false slam_params_file:=$PROJECT_ROOT/config/hanul/slam_toolbox_params.yaml; exec bash"
  CMD_TOP_3="$SETUP_CMD; cd $PROJECT_ROOT && python3 common/lidar_scan_mask.py --ros-args --params-file $PROJECT_ROOT/config/hanul/laser_mask_webots.yaml; exec bash"
  CMD_TOP_4="$CMD_ROBOT_MODEL"
  CMD_BOTTOM_3="$CMD_COLLISION_MONITOR"
  CMD_BOTTOM_4="$CMD_VEL_OUTPUT"
  CMD_RVIZ="$CMD_RVIZ_MAP"
elif [[ "$MODE" == "loc" ]]; then
  TITLE_TOP_1="Webots"
  TITLE_TOP_2="Lidar Mask"
  TITLE_TOP_3="Robot Model"
  TITLE_TOP_4="cmd_vel_output"
  TITLE_BOTTOM_3="Localization"
  TITLE_BOTTOM_4="Nav2"

  CMD_TOP_1="$CMD_WEBOTS"
  CMD_TOP_2="$SETUP_CMD; cd $PROJECT_ROOT && python3 common/lidar_scan_mask.py --ros-args --params-file $PROJECT_ROOT/config/hanul/laser_mask_webots.yaml; exec bash"
  CMD_TOP_3="$CMD_ROBOT_MODEL"
  CMD_TOP_4="$CMD_VEL_OUTPUT"
  CMD_BOTTOM_3="$SETUP_CMD; cd $PROJECT_ROOT && ros2 launch nav2_bringup localization_launch.py map:=$MAP_YAML params_file:=$PROJECT_ROOT/config/hanul/amcl_params.yaml use_sim_time:=false autostart:=True; exec bash"
  CMD_BOTTOM_4="$SETUP_CMD; cd $PROJECT_ROOT && python3 scripts/wait_tf_odom.py 6; python3 scripts/wait_lifecycle_active.py /map_server 20; python3 scripts/wait_lifecycle_active.py /amcl 20; (ros2 launch nav2_bringup navigation_launch.py params_file:=$PROJECT_ROOT/config/hanul/nav2_params.yaml use_sim_time:=false autostart:=True &); python3 scripts/wait_nav2_active.py 30; exec bash"
  CMD_RVIZ="$CMD_RVIZ_LOC"
fi

run_terminator
