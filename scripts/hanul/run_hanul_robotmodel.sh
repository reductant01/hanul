#!/bin/bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
URDF_PATH="${PROJECT_ROOT}/urdf/hanul.urdf"
GENERATED_PARAMS="/tmp/hanul_robot_state_publisher_params.yaml"

if [[ ! -f "$URDF_PATH" ]]; then
  echo "URDF 파일을 찾을 수 없습니다: $URDF_PATH" >&2
  exit 1
fi

{
  echo "/robot_state_publisher:"
  echo "  ros__parameters:"
  echo "    robot_description: |"
  sed 's/^/      /' "$URDF_PATH"
} > "$GENERATED_PARAMS"

echo "Generated params: $GENERATED_PARAMS"

exec ros2 run robot_state_publisher robot_state_publisher --ros-args --params-file "$GENERATED_PARAMS"
