#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
set +u
source /opt/ros/jazzy/setup.bash
set -u
MAP_PATH="${PROJECT_ROOT}/maps/hanul/hanul_map"
ros2 run nav2_map_server map_saver_cli -f "$MAP_PATH" --ros-args \
  --params-file "${PROJECT_ROOT}/config/hanul/map_saver_params.yaml" \
  -p free_thresh_default:=0.25 \
  -p occupied_thresh_default:=0.65
