#!/bin/bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
URDF_TEMPLATE="${PROJECT_ROOT}/urdf/hanul.urdf"
GENERATED_URDF="/tmp/hanul.urdf"
MESH_ROOT_URI="file://${PROJECT_ROOT}"
BASE_MESH_PATH="${PROJECT_ROOT}/assets/hanul/base.stl"
WHEEL_MESH_PATH="${PROJECT_ROOT}/assets/hanul/omni_wheel.stl"

if [[ ! -f "$URDF_TEMPLATE" ]]; then
  echo "URDF 파일을 찾을 수 없습니다: $URDF_TEMPLATE" >&2
  exit 1
fi

is_lfs_pointer() {
  local path="$1"
  [[ -f "$path" ]] && head -n 1 "$path" | grep -q '^version https://git-lfs.github.com/spec/v1$'
}

if [[ -f "$BASE_MESH_PATH" && -f "$WHEEL_MESH_PATH" ]] \
  && ! is_lfs_pointer "$BASE_MESH_PATH" \
  && ! is_lfs_pointer "$WHEEL_MESH_PATH"; then
  sed "s|file:///mnt/hanul|${MESH_ROOT_URI}|g" "$URDF_TEMPLATE" > "$GENERATED_URDF"
else
  cat > "$GENERATED_URDF" <<'EOF'
<?xml version="1.0" ?>
<robot name="hanul">

  <link name="base_footprint"/>

  <link name="base_link">
    <visual>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <geometry><box size="0.28 0.23 0.10"/></geometry>
      <material name="orange"><color rgba="1.0 0.5 0.0 1.0"/></material>
    </visual>
    <collision>
      <origin xyz="0 0 0.05" rpy="0 0 0"/>
      <geometry><box size="0.28 0.23 0.10"/></geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <joint name="joint_base_footprint" type="fixed">
    <parent link="base_footprint"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>

  <link name="wheel_left_link">
    <visual>
      <geometry><cylinder radius="0.05" length="0.03"/></geometry>
      <material name="grey"><color rgba="0.2 0.2 0.2 1"/></material>
    </visual>
    <collision>
      <geometry><cylinder radius="0.05" length="0.03"/></geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="joint_wheel_left" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_left_link"/>
    <origin xyz="0.0664 0.115 0.05" rpy="0 1.5708 -2.0944"/>
    <axis xyz="0 0 1"/>
  </joint>

  <link name="wheel_right_link">
    <visual>
      <geometry><cylinder radius="0.05" length="0.03"/></geometry>
      <material name="grey"><color rgba="0.2 0.2 0.2 1"/></material>
    </visual>
    <collision>
      <geometry><cylinder radius="0.05" length="0.03"/></geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="joint_wheel_right" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_right_link"/>
    <origin xyz="0.0664 -0.115 0.05" rpy="0 1.5708 2.0944"/>
    <axis xyz="0 0 1"/>
  </joint>

  <link name="wheel_back_link">
    <visual>
      <geometry><cylinder radius="0.05" length="0.03"/></geometry>
      <material name="grey"><color rgba="0.2 0.2 0.2 1"/></material>
    </visual>
    <collision>
      <geometry><cylinder radius="0.05" length="0.03"/></geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
  </link>

  <joint name="joint_wheel_back" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_back_link"/>
    <origin xyz="-0.1353 0.0 0.05" rpy="0 1.5708 0"/>
    <axis xyz="0 0 1"/>
  </joint>

</robot>
EOF
  echo "[hanul] STL mesh is unavailable or still a Git LFS pointer. Using fallback geometry." >&2
fi

echo "Using PROJECT_ROOT=$PROJECT_ROOT"
echo "Generated URDF: $GENERATED_URDF"

exec ros2 run robot_state_publisher robot_state_publisher "$GENERATED_URDF"
