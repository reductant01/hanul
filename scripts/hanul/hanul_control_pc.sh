      #!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$PROJECT_ROOT/scripts/hanul/hanul_terminator.sh"

MODE_INPUT="${1:-loc}"
case "$MODE_INPUT" in
  map|mapping)   MODE="control_pc_map" ;;
  loc|localization) MODE="control_pc_loc" ;;
  *)
    echo "사용법: $0 [map|loc]"
    echo "  map: 제어 PC에서 SLAM + RViz + Teleop. NUC에서는 컨트롤러 + 라이다 별도 실행."
    echo "  loc: 제어 PC에서 Map Server + AMCL + Nav2 + RViz + Teleop. NUC에서는 컨트롤러만 실행."
    echo "  NUC와 같은 네트워크, 같은 ROS_DOMAIN_ID 필요."
    exit 1
    ;;
esac

CMD_NUC_REMINDER="echo '=== NUC에서 hanul_nuc.sh 실행 (SSH 접속 후 ./scripts/hanul/hanul_nuc.sh) ===' ; exec bash"

if [[ "$MODE" == "control_pc_map" ]]; then
  TITLE_TOP_1="[NUC] Controller+Lidar"
  CMD_TOP_1="$CMD_NUC_REMINDER"
  TITLE_TOP_2="SLAM Toolbox"
  TITLE_TOP_3="Empty"
  TITLE_TOP_4="Empty"
  TITLE_BOTTOM_3="Empty"
  CMD_TOP_2="$SETUP_CMD; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false slam_params_file:=$PROJECT_ROOT/config/hanul/slam_toolbox_params.yaml; exec bash"
  CMD_TOP_3="$CMD_EMPTY"
  CMD_TOP_4="$CMD_EMPTY"
  CMD_BOTTOM_3="$CMD_EMPTY"
  CMD_BOTTOM_4="$CMD_EMPTY"
  TITLE_BOTTOM_4="Empty"
  CMD_RVIZ="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_MAP_CONFIG; exec bash"
elif [[ "$MODE" == "control_pc_loc" ]]; then
  TITLE_TOP_1="[NUC] Controller+Lidar"
  CMD_TOP_1="$CMD_NUC_REMINDER"
  TITLE_TOP_2="Map Server"
  TITLE_TOP_3="AMCL"
  TITLE_TOP_4="Lifecycle Manager"
  TITLE_BOTTOM_3="Init Pose"
  TITLE_BOTTOM_4="Nav2"
  CMD_TOP_2="$SETUP_CMD; ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=$MAP_YAML; exec bash"
  CMD_TOP_3="$SETUP_CMD; ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=false --params-file $PROJECT_ROOT/config/hanul/amcl_params.yaml; exec bash"
  CMD_TOP_4="$SETUP_CMD; ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p use_sim_time:=false -p autostart:=true -p node_names:=[map_server,amcl]; exec bash"
  CMD_BOTTOM_3="$SETUP_CMD; sleep 3; cd $PROJECT_ROOT && python3 scripts/amcl_pose_estimate.py; exec bash"
  CMD_BOTTOM_4="$SETUP_CMD; ros2 launch nav2_bringup navigation_launch.py params_file:=$PROJECT_ROOT/config/hanul/nav2_params.yaml use_sim_time:=False autostart:=True; exec bash"
  CMD_RVIZ="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_LOC_CONFIG; exec bash"
fi

run_terminator
