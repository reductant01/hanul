# 4. 네비게이션 (Navigation)

목표 지점까지 Nav2로 경로 계획·추종합니다. loc 모드에서 Nav2 터미널이 `navigation_launch.py`로 controller_server, planner_server, bt_navigator, costmap 등을 띄우며 **config/nav2_params.yaml**을 씁니다. 옴니휠은 controller **motion_model: "Omni"**, velocity_smoother에 vy 허용 필수.

---

## RViz 표시 (rviz_loc.rviz)

| 표시 | 역할 |
|------|------|
| Amcl Particle Swarm | AMCL 파티클 (`/particle_cloud`). 수렴 시 한 곳에 뭉침. |
| Global/Local Costmap | 장애물·통행 영역. Global=전체, Local=로봇 주변. |
| Global Plan | 목표까지 경로 (`/plan`). |

**Local Costmap "No map received"**: 처음엔 TF·로봇 위치 미준비로 안 나올 수 있음. 로봇이 조금 움직이면 발행됨. 정상.

**파티클/Costmap 안 보일 때**: 파티클은 Scale(Arrow Length) 키우기, Fixed Frame=map. Local Costmap은 로봇 근처로 줌해서 확인 (작은 창만 그림).

---

## 오류 → 대응

| 현상 | 대응 |
|------|------|
| `observation_sources` / `polygons` / `dock_plugins` 미초기화 | nav2_params.yaml에 collision_monitor용 observation_sources·polygons, docking_server용 dock_plugins·docks 최소 설정 추가. |
| Controller period more then model dt | controller_frequency **20.0** 유지. |
| 목표 보낼 때 AttributeError | orientation에 **x,y,z,w** 네 값 모두 지정. |
| Failed to make progress / Goal ABORTED | motion_model **Omni**, progress_checker 완화. 초기 위치·AMCL·/cmd_vel 확인. |
| /cmd_vel 너무 작음 | AMCL·odom 안정화; [1](01_robot_movement.md)·[3](03_localization.md) 참고. 브릿지 스케일업 옵션. |
| /particle_cloud 타입 경고 | PoseArray 디스플레이만 사용 (Amcl Particle Swarm, `/particle_cloud`). |

---

## 목표 보내기

**RViz**: Nav2 Goal → 맵 위 클릭·방향 드래그.

**터미널**: orientation에 x,y,z,w 모두 지정.

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}"
```

---

[이전: 3. 로컬라이제이션](03_localization.md) · [목차: nav2_usage](nav2_usage.md)
