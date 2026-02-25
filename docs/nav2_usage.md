# Nav2 사용 방법 (한울 프로젝트) — 요약

| 문서 | 내용 |
|------|------|
| [1. 로봇 이동](01_robot_movement.md) | cmd_vel·오도메트리·TF, 오류 대응 |
| [2. 맵핑](02_mapping.md) | SLAM·맵 저장 |
| [3. 로컬라이제이션](03_localization.md) | AMCL·초기 위치·오류 대응 |
| [4. 네비게이션](04_navigation.md) | Nav2·목표·costmap·오류 대응 |

---

## 실행

```bash
cd /mnt/hanul
./start_hanul.sh loc   # 저장 맵 + AMCL + Nav2
./start_hanul.sh map   # SLAM 맵핑
```

- loc: Webots, Map Server, AMCL, Lifecycle, Init Pose, Nav2, RViz, Teleop. 초기 위치는 Init Pose(3초 후) 또는 RViz **2D Pose Estimate**. 목표는 **Nav2 Goal**.
- 설치: `sudo apt install ros-jazzy-nav2-bringup`

---

## config/ YAML

| 파일 | 용도 |
|------|------|
| slam_toolbox_params.yaml | map 모드 — SLAM Toolbox |
| amcl_params.yaml | loc 모드 — AMCL (OmniMotionModel 등) |
| nav2_params.yaml | loc 모드 — Nav2 전반 (controller, costmap, planner 등) |

---

## 자주 나오는 오류 → 대응

| 현상 | 대응 |
|------|------|
| AttributeError (목표 메시지) | orientation에 x,y,z,w 모두 지정. |
| AMCL extrapolation into the future | Webots·컨트롤러 먼저, 몇 초 후 2D Pose Estimate 또는 Init Pose. |
| /cmd_vel 너무 작음 | AMCL·odom 안정화; [1](01_robot_movement.md)·[3](03_localization.md). 브릿지 스케일업. |
| Failed to make progress / ABORTED | motion_model Omni, progress_checker 완화. 초기 위치·AMCL 확인. |
| lidar_link timestamp earlier than transform cache | odom·스캔 동일 stamp 적용됨. |
| particle_cloud 타입 경고 | PoseArray 디스플레이만 사용. |
| collision_monitor / docking_server 초기화 실패 | nav2_params.yaml에 observation_sources·polygons·dock_plugins·docks 설정. [4](04_navigation.md). |
| Controller period more then model dt | controller_frequency 20.0 유지. |

---

## 목표 보내기 (터미널)

```bash
source /opt/ros/jazzy/setup.bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}"
```

---

상세는 [01](01_robot_movement.md) ~ [04](04_navigation.md) 참고.
