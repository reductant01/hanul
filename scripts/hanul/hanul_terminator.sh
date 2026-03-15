# 한울 터미네이터 레이아웃 + hanul_webots.sh / hanul_nuc.sh 공통 변수.
# source 전에 PROJECT_ROOT 설정 필요.

SETUP_CMD="source /opt/ros/jazzy/setup.bash"
WEBOTS_WORLD="${PROJECT_ROOT}/worlds/hanul/hanul.wbt"
MAP_YAML="${PROJECT_ROOT}/maps/hanul/hanul_map.yaml"
RVIZ_MAP_CONFIG="${PROJECT_ROOT}/config/hanul/rviz_map.rviz"
RVIZ_LOC_CONFIG="${PROJECT_ROOT}/config/hanul/rviz_loc.rviz"

CMD_EMPTY="exec bash"
CMD_WEBOTS="deactivate 2>/dev/null; $SETUP_CMD; export PYTHONPATH=$PROJECT_ROOT; webots $WEBOTS_WORLD; exec bash"
CMD_VEL_INPUT="$SETUP_CMD; cd $PROJECT_ROOT && PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH python3 common/cmd_vel_input.py; exec bash"
CMD_COLLISION_MONITOR="$SETUP_CMD; (ros2 run nav2_collision_monitor collision_monitor --ros-args --params-file $PROJECT_ROOT/config/hanul/nav2_params.yaml >> /tmp/collision_monitor.log 2>&1 &); sleep 3; ros2 lifecycle set /collision_monitor configure 2>/dev/null; ros2 lifecycle set /collision_monitor activate 2>/dev/null; exec bash"
CMD_VEL_OUTPUT="$SETUP_CMD; cd $PROJECT_ROOT && PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH python3 -m common.cmd_vel_output; exec bash"
CMD_RVIZ_MAP="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_MAP_CONFIG --ros-args -p use_sim_time:=false; exec bash"
CMD_RVIZ_LOC="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_LOC_CONFIG --ros-args -p use_sim_time:=false; exec bash"


write_terminator_config() {
  local CONFIG_FILE="${1:-/tmp/hanul_terminator_config}"
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
      command = "$CMD_TOP_1"
      title = "$TITLE_TOP_1"
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
      command = "$CMD_VEL_INPUT"
      title = "cmd_vel_input"
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
  echo "$CONFIG_FILE"
}

run_terminator() {
  local CONFIG_FILE
  CONFIG_FILE="$(write_terminator_config)"
  echo "실행 모드: $MODE"
  echo "프로젝트 경로: $PROJECT_ROOT"
  terminator -u -g "$CONFIG_FILE"
}
