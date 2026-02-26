#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$PROJECT_ROOT/scripts/hanul/hanul_terminator.sh"

MODE="robot"
TITLE_TOP_1="Controller (Real)"
CMD_TOP_1="$CMD_REAL_CONTROLLER"
TITLE_TOP_2="Map Server"
TITLE_TOP_3="AMCL"
TITLE_TOP_4="Lifecycle Manager"
TITLE_BOTTOM_3="Init Pose"
TITLE_BOTTOM_4="Nav2"
CMD_TOP_2="$SETUP_CMD; ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=$MAP_YAML; exec bash"
CMD_TOP_3="$SETUP_CMD; ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=false --params-file $PROJECT_ROOT/config/amcl_params.yaml; exec bash"
CMD_TOP_4="$SETUP_CMD; ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p use_sim_time:=false -p autostart:=true -p node_names:=[map_server,amcl]; exec bash"
CMD_BOTTOM_3="$SETUP_CMD; sleep 3; ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped '{header: {frame_id: map}, pose: {pose: {position: {x: $INIT_X, y: $INIT_Y, z: 0.0}, orientation: {z: $INIT_QZ, w: $INIT_QW}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0685]}}'; exec bash"
CMD_BOTTOM_4="$SETUP_CMD; ros2 launch nav2_bringup navigation_launch.py params_file:=$PROJECT_ROOT/config/nav2_params.yaml use_sim_time:=False autostart:=True; exec bash"
CMD_RVIZ="$SETUP_CMD; ros2 run rviz2 rviz2 -d $RVIZ_LOC_CONFIG; exec bash"

run_terminator
