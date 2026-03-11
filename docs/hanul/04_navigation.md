# 4. 네비게이션 (Navigation)

---

## 1. RViz lidar_link 드롭 / costmap 미갱신

**오류:** `Message Filter dropping message: frame 'lidar_link'`, global/local costmap이 안 나오거나 갱신 안 됨.

**이유:** costmap·스캔은 map→odom→base_footprint→lidar_link TF가 필요한데, map→odom은 AMCL이 스캔 처리 **뒤**에만 발행돼서 그 시점에는 TF가 없음.

**수정:** 스캔과 같은 stamp로 **map→odom identity**를 컨트롤러에서 보조 발행. (`common/map_odom_identity.py`)

---

## 2. amcl_pose_estimate.py

**오류 (2.1):** No AMCL pose. QoS 불일치로 `/amcl_pose` 구독 안 됨.

**이유:** AMCL은 BEST_EFFORT 등으로 발행하는데 스크립트가 RELIABLE만 구독하면 토픽이 맞지 않아 구독 실패.

**수정:** RELIABLE·BEST_EFFORT 각각 TRANSIENT_LOCAL로 구독하고, 구독 후 1초 대기한 뒤 타임아웃 카운트.

**오류 (2.2):** "Failed to transform initial pose (extrapolation into the future)". odom TF 시각이 초기 포즈보다 뒤에 있음.

**이유:** 컨트롤러가 막 올라온 직후라 odom TF가 아직 없거나 시각이 초기 포즈보다 늦음.

**수정:** `Setting pose`가 이어지면 무시. Webots·컨트롤러 먼저 켠 뒤 몇 초 후에 초기 포즈 실행.

---

## 3. Transform data too old (map → odom)

**오류:** controller_server에서 map→odom을 "too old"로 버려 목표 실행이 안 됨.

**이유:** FollowPath의 `transform_tolerance`가 작아서, 지연이 조금만 있어도 "too old"로 판단함.

**수정:** `config/hanul/nav2_params.yaml`의 FollowPath에서 `transform_tolerance`를 5.0 이상(필요 시 10.0)으로 설정.

---

## 4. Costmap 미표시 (No map received)

**오류:** Global/Local Costmap이 안 나오고 "No map received". `Invalid frame ID "odom"`, `Timed out waiting for transform from base_footprint to odom`.

**이유:** Costmap은 odom TF가 있어야 맵을 만들고 발행함. Nav2가 컨트롤러보다 먼저 떠서, 기동 시점에는 아직 odom이 없음.

**수정:** `hanul_webots.sh` loc 모드에서 Nav2 실행 전에 `scripts/wait_for_odom.py 6` 실행. 재생(▶)을 6초 안에 누르면 costmap이 뜸.

---

## 5. 파티클 클라우드가 RViz에 안 나옴

**오류:** AMCL은 동작하는데 RViz에 파티클 구름(particle cloud)이 보이지 않음.

**이유:** RViz에 **ParticleCloud** 디스플레이를 넣었더라도, 디스플레이 타입이나 토픽 경로가 잘못되면 안 보임. AMCL이 발행하는 토픽은 **`/particle_cloud`** 하나뿐이므로, 디스플레이의 Topic 값이 정확히 `/particle_cloud`여야 함. PoseArray가 아니라 **nav2_rviz_plugins의 ParticleCloud** 타입을 써야 함.

**수정:** RViz에서 **By display type**으로 **ParticleCloud**(nav2_rviz_plugins/ParticleCloud) 디스플레이를 추가한 뒤, Topic을 **`/particle_cloud`**로 지정. `rviz_loc.rviz`에는 이미 이렇게 설정돼 있음. 초기 위치(2D Pose Estimate 또는 amcl_pose_estimate.py)를 한 번 준 뒤에는 AMCL이 파티클을 발행해 화면에 보임.

---

## 6. Nav2 패널에서 Localization / Navigation이 inactive

**오류:** 로컬라이제이션·네비게이션은 동작하는데 Nav2 패널에 Localization 또는 Navigation이 inactive로만 표시됨.

**이유:** 패널은 **노드 이름**이 `lifecycle_manager_localization`(로컬라이제이션), `lifecycle_manager_navigation`(네비게이션)인 lifecycle 매니저만 인식함. 이름이 다르면 실제로는 동작해도 inactive로만 보임.

**수정:** map_server·amcl을 관리하는 lifecycle 매니저 실행 시 `-r __node:=lifecycle_manager_localization` 추가. (`hanul_webots.sh`에 반영됨.) Navigation은 `navigation_launch.py` 기동이 끝날 때까지 대기하면 active로 바뀜.

---

## 7. RViz 디스플레이·토픽 정리 (누가 발행하고, 어디서 쓰는지)

- **Costmap (local_costmap, global_costmap)**  
  **발행:** Nav2의 costmap_2d 노드들. `navigation_launch.py`로 올라오는 controller 쪽에서 local_costmap·global_costmap을 계산해 `/local_costmap/costmap`, `/global_costmap/costmap` 등으로 발행함.  
  **우리 사용처:** 우리가 직접 구독하는 건 아님. Nav2 **controller_server**가 이 costmap을 읽어서 경로 추종·장애물 회피 시 “어디가 막혀 있는지” 판단하고, 그 결과를 cmd_vel로 내보냄. RViz는 같은 토픽을 구독해서 **화면에만** 그려 줌.

- **Map (/map)**  
  **발행:** **nav2_map_server** (map_server 노드). `hanul_webots.sh` loc 모드의 Map Server 탭에서 띄움.  
  **사용처:** AMCL이 로컬라이제이션할 때 맵으로 사용하고, Nav2 planner가 경로 계획할 때 사용함. RViz는 `/map`을 구독해 배경 맵으로 표시함.

- **LaserScan (/scan)**  
  **발행:** 우리 **컨트롤러**(Webots/NUC)가 라이다 데이터를 받아 `ros_bridge.publish_scan()`으로 발행함.  
  **사용처:** SLAM Toolbox(맵핑), AMCL(로컬라이제이션), Nav2 costmap(장애물 레이어), nav2_collision_monitor(전방 정지/감속)가 구독해서 씀. RViz는 시각화용.

- **ParticleCloud (/particle_cloud)**  
  **발행:** **AMCL**. 초기 pose를 받은 뒤 파티클 필터가 돌면서 발행함.  
  **사용처:** RViz에서만 구독해서 “로컬라이제이션 신뢰도/분포”를 화면에 보여 줌. 우리 코드에서는 구독하지 않음.

- **Path (/plan)**  
  **발행:** Nav2의 **planner**(예: NavfnPlanner). 목표를 받으면 global costmap 위에서 경로를 계산해 발행함.  
  **사용처:** Nav2 **controller_server**가 이 경로를 따라 cmd_vel을 만듦. RViz는 `/plan`을 구독해 “계획된 경로”를 녹색 선으로 표시함.

- **TF**  
  **발행:** map→odom은 **AMCL**, odom→base_footprint 등은 우리 **컨트롤러**(tf_converter), map→odom 보조는 **map_odom_identity**, lidar_link 등도 컨트롤러.  
  **사용처:** 모든 노드가 좌표 변환할 때 사용. RViz는 TF를 구독해 축/프레임을 화면에 그림.

- **Grid**  
  RViz **내장** 참조용. 토픽 발행 없음.

---

## 8. Collision Monitor가 있어도 속도가 줄지 않을 때

**현상:** 스캔이 PolygonSlow/PolygonStop 범위 안에 들어와도 로봇 속도가 감속/정지하지 않음.

**우리 설정 요약**

- Collision Monitor 설정은 별도 `collision_monitor_params.yaml`이 아니라 **`config/hanul/nav2_params.yaml`** 의 `collision_monitor:` 블록에 있음. loc 모드에서 `navigation_launch.py`가 이 파일을 쓰므로 **설정은 로드됨**.
- Jazzy 기준 **nav2_bringup의 `navigation_launch.py`** 에는 Velocity Smoother가 `cmd_vel_smoothed`→`cmd_vel` 리매핑이 **없고**, Collision Monitor가 **이미 포함**되어 있음.  
  흐름: Controller → `cmd_vel_nav` → Velocity Smoother → `cmd_vel_smoothed` → Collision Monitor → `cmd_vel` → 로봇(ros_bridge).  
  따라서 **“Nav2 stack 준비”(리매핑 제거)는 Jazzy에서는 이미 만족**된 상태임.

**점검할 것**

1. **loc 모드에서만 적용**  
   맵 전용(Teleop만)일 때는 Collision Monitor 탭을 켜야 하고, Teleop은 `cmd_vel_smoothed`로 발행해야 Collision Monitor를 경유함. loc 모드(Nav2 사용)에서는 launch에 Collision Monitor가 포함되어 있으므로 별도 탭 없이 동작해야 함.

2. **TF**  
   Collision Monitor는 `/scan`을 `base_footprint` 기준으로 폴리곤 안의 점 개수를 셈. **`base_footprint` ↔ 스캔 프레임(예: `lidar_link`) TF**가 있어야 함.  
   `ros2 run tf2_ros tf2_echo base_footprint lidar_link` 로 TF 존재·지연 확인.

3. **/scan 토픽**  
   `observation_sources`의 `topic: "scan"`과 실제 발행 토픽이 일치하는지, `ros2 topic echo /scan --once` 로 메시지가 오는지 확인.

4. **min_points**  
   `PolygonSlow`/`PolygonStop`는 각각 **4점 이상**이 폴리곤 안에 들어와야 감속/정지함. 스캔이 성기거나 폴리곤이 작으면 4점 미만일 수 있음. 필요하면 `min_points`를 2 등으로 낮춰 보기.

5. **실제로 cmd_vel이 바뀌는지**  
   장애물을 범위 안에 넣은 상태에서 `ros2 topic echo /cmd_vel` 로 출력이 감소/0이 되는지 확인. 변하지 않으면 Collision Monitor가 동작하지 않거나 TF·min_points를 점검.

---

## 9. Collision Monitor → cmd_vel 직결

**현재 구성**

- Teleop(예: `common/teleop_keyboard_hold.py`)은 **`cmd_vel_smoothed`** 에 발행.
- Collision Monitor는 `cmd_vel_smoothed`를 구독해 감속/정지 처리 후 **`cmd_vel`** 에 발행. 로봇은 **`cmd_vel`** 만 구독.
- escape 노드는 사용하지 않음. Stop 구역에서는 후진 포함 모두 정지.

참고: [Using Collision Monitor — Nav2](https://docs.nav2.org/tutorials/docs/using_collision_monitor.html).

---

[이전: 3. 로컬라이제이션](03_localization.md) · [다음: 5. NUC 실제 로봇](05_nuc.md)
