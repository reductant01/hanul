#!/bin/bash

set -euo pipefail

MODE_INPUT="${1:-loc}"
case "$MODE_INPUT" in
  map|mapping)
    MODE="map"
    ;;
  loc|localization)
    MODE="loc"
    ;;
  *)
    echo "사용법: $0 [map|loc]"
    exit 1
    ;;
esac

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SETUP_CMD="source /opt/ros/jazzy/setup.bash"
WEBOTS_WORLD="$PROJECT_ROOT/worlds/hanul.wbt"
MAP_YAML="$PROJECT_ROOT/maps/hanul_map.yaml"
RVIZ_MAP_CONFIG="$PROJECT_ROOT/config/rviz_map.rviz"
RVIZ_LOC_CONFIG="$PROJECT_ROOT/config/rviz_loc.rviz"

# loc 모드 초기 자세 (map 좌표계 기준)
INIT_X=0.0
INIT_Y=0.0
INIT_YAW=0.0
INIT_QZ="$(python3 -c "import math; print(math.sin($INIT_YAW / 2.0))")"
INIT_QW="$(python3 -c "import math; print(math.cos($INIT_YAW / 2.0))")"

CMD_EMPTY="exec bash"
CMD_WEBOTS="$SETUP_CMD; webots $WEBOTS_WORLD; exec bash"
CMD_TELEOP="$SETUP_CMD; ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.8 -p turn:=1.0; exec bash"

if [[ "$MODE" == "map" ]]; then
  TITLE_TOP_2="SLAM Toolbox"
  TITLE_TOP_3="Empty"
  TITLE_TOP_4="Empty"
  TITLE_BOTTOM_3="Empty"
  CMD_TOP_2="$SETUP_CMD; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false slam_params_file:=$PROJECT_ROOT/config/slam_toolbox_params.yaml; exec bash"
  CMD_TOP_3="$CMD_EMPTY"
  CMD_TOP_4="$CMD_EMPTY"
  CMD_BOTTOM_3="$CMD_EMPTY"
  CMD_BOTTOM_4="$CMD_EMPTY"
  TITLE_BOTTOM_4="Empty"
  CMD_RVIZ="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_MAP_CONFIG; exec bash"
elif [[ "$MODE" == "loc" ]]; then
  TITLE_TOP_2="Map Server"
  TITLE_TOP_3="AMCL"
  TITLE_TOP_4="Lifecycle Manager"
  TITLE_BOTTOM_3="Init Pose"
  TITLE_BOTTOM_4="Nav2"
  CMD_TOP_2="$SETUP_CMD; ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=$MAP_YAML; exec bash"
  CMD_TOP_3="$SETUP_CMD; ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=false -p scan_topic:=/scan -p base_frame_id:=base_footprint -p odom_frame_id:=odom -p global_frame_id:=map -p update_min_d:=0.02 -p update_min_a:=0.02; exec bash"
  CMD_TOP_4="$SETUP_CMD; ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p use_sim_time:=false -p autostart:=true -p node_names:=[map_server,amcl]; exec bash"
  CMD_BOTTOM_3="$SETUP_CMD; sleep 3; ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped '{header: {frame_id: map}, pose: {pose: {position: {x: $INIT_X, y: $INIT_Y, z: 0.0}, orientation: {z: $INIT_QZ, w: $INIT_QW}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0685]}}'; exec bash"
  CMD_BOTTOM_4="$SETUP_CMD; ros2 launch nav2_bringup navigation_launch.py params_file:=$PROJECT_ROOT/config/nav2_params.yaml use_sim_time:=False autostart:=True; exec bash"
  CMD_RVIZ="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_LOC_CONFIG; exec bash"
fi

CONFIG_FILE="/tmp/hanul_terminator_config"
cat <<EOF > "$CONFIG_FILE"
[global_config]
  suppress_multiple_term_dialog = True
[keybindings]
[profiles]
  [[default]]
    use_system_font = False
    font = Ubuntu Mono 12
    scrollback_infinite = True
[layouts]
  [[default]]
    [[[window0]]]
      type = Window
      parent = ""
    [[[root_split]]]
      type = VPaned
      parent = window0
      position = 500

    [[[top_h1]]]
      type = HPaned
      parent = root_split
      position = 480
    [[[top_h2]]]
      type = HPaned
      parent = top_h1
      position = 480
    [[[top_h3]]]
      type = HPaned
      parent = top_h1
      position = 480

    [[[bottom_h1]]]
      type = HPaned
      parent = root_split
      position = 480
    [[[bottom_h2]]]
      type = HPaned
      parent = bottom_h1
      position = 480
    [[[bottom_h3]]]
      type = HPaned
      parent = bottom_h1
      position = 480

    [[[terminal_top_1]]]
      type = Terminal
      parent = top_h2
      order = 0
      profile = default
      command = "$CMD_WEBOTS"
      title = "Webots"
    [[[terminal_top_2]]]
      type = Terminal
      parent = top_h2
      order = 1
      profile = default
      command = "$CMD_TOP_2"
      title = "$TITLE_TOP_2"
    [[[terminal_top_3]]]
      type = Terminal
      parent = top_h3
      order = 0
      profile = default
      command = "$CMD_TOP_3"
      title = "$TITLE_TOP_3"
    [[[terminal_top_4]]]
      type = Terminal
      parent = top_h3
      order = 1
      profile = default
      command = "$CMD_TOP_4"
      title = "$TITLE_TOP_4"

    [[[terminal_bottom_1]]]
      type = Terminal
      parent = bottom_h2
      order = 0
      profile = default
      command = "$CMD_RVIZ"
      title = "RViz2"
    [[[terminal_bottom_2]]]
      type = Terminal
      parent = bottom_h2
      order = 1
      profile = default
      command = "$CMD_TELEOP"
      title = "Teleop"
    [[[terminal_bottom_3]]]
      type = Terminal
      parent = bottom_h3
      order = 0
      profile = default
      command = "$CMD_BOTTOM_3"
      title = "$TITLE_BOTTOM_3"
    [[[terminal_bottom_4]]]
      type = Terminal
      parent = bottom_h3
      order = 1
      profile = default
      command = "$CMD_BOTTOM_4"
      title = "$TITLE_BOTTOM_4"
EOF

echo "실행 모드: $MODE"
echo "프로젝트 경로: $PROJECT_ROOT"
terminator -u -g "$CONFIG_FILE"
