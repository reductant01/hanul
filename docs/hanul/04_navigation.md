# 4. 네비게이션 (Navigation)

---

## Nav2 사용 순서 (공식 문서 권장)

1. **Nav2·로봇(Webots/NUC) 기동** 후 RViz에서 loc 설정 로드.
2. **2D Pose Estimate** 버튼 선택 → 맵에서 **로봇이 실제로 있는 위치**를 클릭한 뒤, **방향**을 드래그로 설정. (초기 위치를 주지 않으면 로봇 위치를 모르므로 TF 트리가 완성되지 않고 목표 동작이 불안정함.)
3. **로봇과 파티클 구름(Amcl Particle Swarm)** 이 맵 위에 보이고, TF 트리가 이어졌는지 확인한 뒤 **그 다음에** 목표 전송.
4. **Nav2 Goal** 버튼 선택 → 맵에서 목표 지점 클릭·드래그로 방향 설정. 경로가 생성되면 로봇이 이동함.

초기 포즈를 설정하지 않거나 잘못된 위치에 두면 map→odom·AMCL이 틀어져 경로는 나와도 cmd_vel이 거의 0이 되거나 회전만 할 수 있음.

---

## 1. observation_sources / polygons / dock_plugins 미초기화

**오류:** config/hanul/nav2_params.yaml 관련해 observation_sources, polygons, dock_plugins 미초기화 오류.

**수정:** config/hanul/nav2_params.yaml에 collision_monitor용 observation_sources·polygons, docking_server용 dock_plugins·docks 최소 설정 추가.

---

## 2. Controller period more then model dt

**오류:** 컨트롤러 주기가 모델 dt보다 크다는 경고.

**수정:** controller_frequency를 **20.0**으로 유지.

---

## 3. 목표 보낼 때 AttributeError

**오류:** 목표 지점 전송 시 orientation 관련 AttributeError.

**수정:** orientation에 **x, y, z, w** 네 값 모두 지정.

---

## 4. Failed to make progress / Goal ABORTED

**오류:** 목표까지 진행 실패 또는 목표 중단.

**수정:** motion_model **Omni** 사용, progress_checker 완화. 초기 위치·AMCL·/cmd_vel 동작 확인.

---

## 5. /cmd_vel 너무 작음

**오류:** Nav2가 보낸 속도가 로봇에 너무 작게 전달됨.

**수정:** AMCL·odom 안정화 후 [1](01_robot_movement.md)·[3](03_localization.md) 참고. ros_bridge 스케일업 옵션 사용.

---

## 6. /particle_cloud 타입 경고

**오류:** particle_cloud 토픽 타입 관련 경고.

**수정:** PoseArray 디스플레이만 사용(Amcl Particle Swarm, `/particle_cloud`).

---

## 7. Transform data too old (map → odom)

**오류:** controller_server에서 "Transform data too old when converting from map to odom" ERROR. Data time이 Transform time보다 수 초 앞서 있어 map→odom TF를 버리고, 원점 이동 등 목표 실행이 안 됨.

**수정:** `config/hanul/nav2_params.yaml`의 controller_server → FollowPath에서 `transform_tolerance`를 **0.1 → 5.0**으로 상향. map→odom이 최대 5초까지 지연돼도 사용하도록 함. 계속 오류 나면 10.0까지 올려서 사용.

---

## 8. collision_monitor 스캔 타임스탬프 경고

**오류:** collision_monitor에서 "[scan]: Latest source and current collision monitor node timestamps differ on X seconds. Ignoring the source." WARN. 스캔 타임스탬프와 노드 시간 차이로 스캔을 무시함.

**수정:** `config/hanul/nav2_params.yaml`의 collision_monitor에서 `transform_tolerance`를 **0.2 → 10.0**으로, `source_timeout: 15.0` 추가. 타임스탬프 차이가 있어도 소스를 버리지 않도록 완화.

---

## 9. RViz lidar_link 드롭 / Local Costmap 오류

**오류:** RViz에서 "Message Filter dropping message: frame 'lidar_link' ... the timestamp on the message is earlier than all the data in the transform cache" 반복, Local Costmap 디스플레이에 주황색 느낌표. 스캔 타임스탬프가 TF 캐시보다 과거라 메시지가 버려지고 costmap이 갱신되지 않음.

**수정:** RViz LaserScan Tolerance를 **10.0**으로 설정(`config/hanul/rviz_map.rviz`, `config/hanul/rviz_loc.rviz`). Nav2 costmap이 스캔을 수용하도록 local_costmap의 voxel_layer, global_costmap의 obstacle_layer에 **tf_filter_tolerance: 10.0** 추가(`config/hanul/nav2_params.yaml`).

---

## 10. 경로는 나오는데 cmd_vel이 거의 0만 나옴 / 로봇이 직진하지 않고 회전만 함

**오류:** planner는 경로를 생성하는데, `/cmd_vel`에 linear.x·linear.y·angular.z가 0.001 수준으로만 나와 로봇이 거의 안 움직이거나 회전만 함.

**원인:** (1) controller_server의 **local_costmap**이 활성화 실패("rcl node's context is invalid")로 동작하지 않아, 컨트롤러가 유효한 속도 명령을 내지 못함. (2) map→odom **TF 오류**(Transform data too old)로 로봇 위치를 못 써서 보수적으로 거의 0만 출력.

**수정:** (1) Nav2를 **한 번만** 기동하고, 모든 노드 활성화가 끝난 뒤에만 목표 전송. 기동 중 Ctrl+C 후 바로 재실행하지 말 것. (2) §7·§9의 transform_tolerance, tf_filter_tolerance 적용으로 TF/스캔 수신 상태 확인. (3) 임시 완화: `common/ros_bridge.py`에서 **cmd_vel_scale_thresh_linear**, **cmd_vel_scale_thresh_angular**를 **0.01**로 낮춰, 아주 작은 cmd_vel도 스케일(×30)이 적용되도록 함. 근본 해결은 local_costmap·TF 정상화.

---

[이전: 3. 로컬라이제이션](03_localization.md) · [다음: 5. NUC 실제 로봇](05_nuc.md)
