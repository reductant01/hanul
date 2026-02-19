#!/bin/bash

# ==============================================================================
# 1. 경로 자동 감지 및 명령어 설정
# ==============================================================================

# [핵심] 현재 스크립트가 있는 폴더 위치를 절대 경로로 찾아냅니다.
# 다른 컴퓨터나 USB에서 실행해도 경로가 깨지지 않게 해주는 코드입니다.
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "📂 프로젝트 위치 감지됨: $PROJECT_ROOT"

# ROS 2 환경 설정 명령어 (Jazzy 기준)
SETUP_CMD="source /opt/ros/jazzy/setup.bash"

# [1] 왼쪽 위: Webots 실행
#     (자동 감지된 경로를 사용하여 월드 파일을 엽니다)
WEBOTS_WORLD="$PROJECT_ROOT/worlds/hanul.wbt"
CMD_1="$SETUP_CMD; webots \"$WEBOTS_WORLD\"; exec bash"

# [2] 오른쪽 위: SLAM Toolbox 실행 (맵 갱신 주기 단축용 커스텀 파라미터 사용)
CMD_2="$SETUP_CMD; ros2 launch slam_toolbox online_async_launch.py use_sim_time:=false slam_params_file:=$PROJECT_ROOT/config/slam_toolbox_params.yaml; exec bash"

# [3] 왼쪽 아래: RViz2 실행
CMD_3="$SETUP_CMD; ros2 run rviz2 rviz2; exec bash"

# [4] 오른쪽 아래: 키보드 컨트롤러 실행
CMD_4="$SETUP_CMD; ros2 run teleop_twist_keyboard teleop_twist_keyboard; exec bash"


# ==============================================================================
# 2. Terminator 임시 설정 파일 생성 (/tmp 폴더 사용)
# ==============================================================================
# 컴퓨터의 기존 설정을 건드리지 않고, 임시로 4분할 화면 설정을 만듭니다.

CONFIG_FILE="/tmp/hanul_terminator_config"

cat <<EOF > $CONFIG_FILE
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
    [[[child1]]]
      type = VPaned
      parent = window0
      position = 500
    [[[child2]]]
      type = HPaned
      parent = child1
      position = 960
    [[[child3]]]
      type = HPaned
      parent = child1
      position = 960

    [[[terminal_top_left]]]
      type = Terminal
      parent = child2
      order = 0
      profile = default
      command = "$CMD_1"
      title = "Webots"
    [[[terminal_top_right]]]
      type = Terminal
      parent = child2
      order = 1
      profile = default
      command = "$CMD_2"
      title = "SLAM Toolbox"
    [[[terminal_bottom_left]]]
      type = Terminal
      parent = child3
      order = 0
      profile = default
      command = "$CMD_3"
      title = "RViz2"
    [[[terminal_bottom_right]]]
      type = Terminal
      parent = child3
      order = 1
      profile = default
      command = "$CMD_4"
      title = "Teleop Controller"
EOF

# ==============================================================================
# 3. Terminator 실행 (설정 파일 적용)
# ==============================================================================
# -g 옵션: 지정한 설정 파일을 사용하여 실행
# -u, -m: 기존 터미네이터 프로세스와 섞이지 않게 독립적으로 실행

terminator -u -g $CONFIG_FILE
