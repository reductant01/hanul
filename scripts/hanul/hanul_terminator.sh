# 한울 터미네이터 레이아웃 + hanul_webots.sh / hanul_nuc.sh 공통 변수.
# source 전에 PROJECT_ROOT 설정 필요.

SETUP_CMD="source /opt/ros/jazzy/setup.bash"
WEBOTS_WORLD="${PROJECT_ROOT}/worlds/hanul/hanul.wbt"
MAP_YAML="${PROJECT_ROOT}/maps/hanul/hanul_map.yaml"
RVIZ_MAP_CONFIG="${PROJECT_ROOT}/config/hanul/rviz_map.rviz"
RVIZ_LOC_CONFIG="${PROJECT_ROOT}/config/hanul/rviz_loc.rviz"

INIT_X=0.0
INIT_Y=0.0
INIT_YAW=0.0
INIT_QZ="$(python3 -c "import math; print(math.sin($INIT_YAW / 2.0))")"
INIT_QW="$(python3 -c "import math; print(math.cos($INIT_YAW / 2.0))")"

CMD_EMPTY="exec bash"
CMD_WEBOTS="deactivate 2>/dev/null; $SETUP_CMD; export PYTHONPATH=$PROJECT_ROOT; webots $WEBOTS_WORLD; exec bash"
CMD_TELEOP="$SETUP_CMD; ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.8 -p turn:=0.5; exec bash"
CMD_REAL_CONTROLLER="$SETUP_CMD; cd $PROJECT_ROOT/controllers/hanul_controller_nuc && PYTHONPATH=$PROJECT_ROOT:\$PYTHONPATH python3 hanul_controller_nuc.py; exec bash"
CMD_LIDAR_A1="$SETUP_CMD; echo 'A1 라이다: 아래에 드라이버 명령 실행 (예: ros2 run ... /scan 발행)'; exec bash"

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
  echo "$CONFIG_FILE"
}

run_terminator() {
  local CONFIG_FILE
  CONFIG_FILE="$(write_terminator_config)"
  echo "실행 모드: $MODE"
  echo "프로젝트 경로: $PROJECT_ROOT"
  terminator -u -g "$CONFIG_FILE"
}
