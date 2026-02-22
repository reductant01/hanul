# Nav2 사용 방법 (한울 프로젝트)

## 1. 패키지 설치

loc 모드에서 Nav2를 쓰려면 bringup 패키지가 필요합니다.

```bash
sudo apt update
sudo apt install ros-jazzy-nav2-bringup
```

## 2. 예제 대비: 우리가 한 것·따라 할 순서

공식 예제는 **Gazebo + Turtlebot**으로 “실행 예제”를 돌리지만, **한울은 Webots + start_hanul.sh loc**으로 같은 역할을 합니다. RViz 화면은 예제와 동일하게 **맵 → 초기 위치(2D Pose Estimate) → Nav2 Goal → 경로·주행** 순으로 맞추면 됩니다.

| 예제 단계 | 한울에서 한 것 | 화면에서 확인할 것 |
|-----------|----------------|---------------------|
| **1) Install** | `ros-jazzy-nav2-bringup` 설치 | — |
| **2) Run the Example** | `./start_hanul.sh loc` 실행 (Webots, Map Server, AMCL, Lifecycle, Init Pose, **Nav2**, RViz, Teleop 한 번에) | Webots 3D 창 + 터미널 여러 개 + **RViz**가 뜸 |
| **3) RViz에 맵 나오기** | Map Server가 `hanul_map.yaml` 로드 → RViz의 **Map** 디스플레이에 맵 표시 | RViz 왼쪽 Displays에 Map 체크, **Fixed Frame: map**, 맵(흰/회색 영역) 보임 |
| **4) 초기 위치 주기** | **Init Pose** 터미널이 3초 후 `/initialpose` 한 번 발행 (0,0). 또는 RViz **2D Pose Estimate**로 직접 클릭·드래그 | 맵 위에 **로봇 포즈(초록 화살표)**·**AMCL 파티클**이 보이고, Global Status가 **Ok**으로 바뀜 |
| **5) Nav2 활성** | Lifecycle으로 map_server·amcl 활성, Nav2 터미널로 controller·planner·bt_navigator 기동 | `ros2 action list`에 `/navigate_to_pose` 있음. RViz에 **Navigation 2** 플러그인(Startup 완료) |
| **6) 목표 주기** | RViz **Nav2 Goal** 버튼 → 맵 위 목표 점 클릭·방향 드래그. 또는 터미널 `ros2 action send_goal /navigate_to_pose ...` | 맵 위 **초록 목표 화살표** + **보라색/파란 경로선** + 로봇이 움직임 |
| **7) 로봇 주행** | Controller가 경로 추종 → `/cmd_vel` → Webots 로봇 구동 | Webots에서 로봇 이동, RViz에서 로봇·경로·costmap 갱신 |

**지금 우리가 어디까지 했는지:**  
- **1~2**: 설치·실행 구조는 완료 (loc 모드로 한 번에 띄움).  
- **3~4**: 맵·초기 위치는 Map Server + Init Pose(또는 2D Pose Estimate)로 가능.  
- **5**: Nav2는 `navigation_launch.py` + `nav2_params.yaml`로 띄우고, collision_monitor·docking_server 등 초기화 오류는 수정해 둠.  
- **6~7**: 목표를 주면 경로 생성·follow_path까지 되도록 MPPI Omni·progress_checker 완화 등 적용해 둠.  

**예제처럼 따라 하려면:**  
1. `./start_hanul.sh loc` 실행 후 **모든 터미널이 에러 없이 떠 있는지** 확인 (특히 Nav2).  
2. **RViz**가 `config/rviz_loc.rviz`로 열리면, **Map**이 보이는지, **Fixed Frame: map**인지 확인.  
3. 초기 위치가 어긋나 있으면 RViz에서 **2D Pose Estimate**로 로봇이 서 있는 곳을 다시 찍기.  
4. **Nav2 Goal** 버튼으로 맵 위 목표를 찍고 방향 드래그 → 경로가 생기고 로봇이 움직이는지 확인.  
5. 터미널로 목표만 보내고 싶으면 아래 §5의 `ros2 action send_goal /navigate_to_pose ...` 사용.

## 3. loc 모드로 실행

### 실행 순서 (한 번에 보기)

1. **프로젝트 디렉터리로 이동**
   ```bash
   cd /mnt/hanul
   ```

2. **loc 모드 실행** (Webots, 맵·AMCL·Nav2·RViz·Teleop 등 한 번에 뜸)
   ```bash
   ./start_hanul.sh loc
   ```

3. **창 확인**  
   - **Webots**: 3D 월드와 로봇.  
   - **터미널**: Map Server, AMCL, Lifecycle Manager, Init Pose, Nav2, (RViz), Teleop. **Nav2** 탭에 에러가 없어야 함.  
   - **RViz**: 맵이 보이고, Displays에 Map·Amcl Particle Swarm·LaserScan 등 체크.

4. **초기 위치**  
   - Init Pose 터미널이 3초 후 (0,0)으로 한 번 보냄.  
   - 위치가 어긋나면 RViz **2D Pose Estimate** 클릭 → 맵에서 로봇 위치 클릭 후 방향 드래그.

5. **목표 주기 (둘 중 하나)**  
   - **RViz**: 상단 **Nav2 Goal** 클릭 → 맵 위 목표 지점 클릭 → 방향 드래그.  
   - **터미널** (새 터미널에서):
     ```bash
     source /opt/ros/jazzy/setup.bash
     ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
       "pose: {header: {frame_id: 'map'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"
     ```

6. **동작 확인**  
   - RViz에서 경로(보라/파란 선)와 로봇 이동. Webots에서 로봇이 같은 방향으로 이동.

---

- **Map Server**: 맵 로드. **AMCL**: 위치 추정. **Lifecycle Manager**: map_server·amcl 활성화. (nav2_params 미사용, 예전처럼 ros2 run으로만 실행.)
- **Init Pose**: 3초 후 맵 원점(0,0)으로 초기 위치 한 번 발행.
- **Nav2**: controller·planner·bt_navigator만 실행 (navigation_launch + nav2_params.yaml). 목표 전송·장애물 회피용.
- RViz에서 **2D Pose Estimate**로 초기 위치를 다시 줄 수 있습니다.
- **Teleop** 터미널: 키보드로 수동 조종합니다.

## 4. 네비게이션 동작 확인

목표를 보내기 전에 **Nav2가 떠 있어야** 합니다. `start_hanul.sh loc` 실행 시 **Nav2** 탭(BOTTOM_4)이 켜져 있어야 하고, 에러 없이 실행 중이어야 합니다.

**액션 서버가 있는지 확인:**

```bash
source /opt/ros/jazzy/setup.bash
ros2 action list
```

출력에 `/navigate_to_pose`가 보이면 Nav2가 준비된 상태입니다. 없으면 "Waiting for an action server to become available..."에서 계속 대기하게 됩니다.

**노드로 확인:**

```bash
ros2 node list | grep -E "bt_navigator|controller_server|planner_server"
```

위 노드들이 보이면 Nav2가 동작 중입니다. 안 보이면 Nav2 터미널을 켜고, 터미널에 에러가 없는지 확인한 뒤 다시 시도합니다.

## 5. 특정 좌표로 이동 (원점 또는 임의 점)

목표 포즈를 보내면 Nav2가 경로를 짜고 주행합니다.

**원점 (0, 0)으로 이동:**

```bash
source /opt/ros/jazzy/setup.bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "pose: {header: {frame_id: 'map'}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"
```

**다른 좌표 (예: x=1.0, y=0.5)로 이동:**

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {w: 1.0}}}"
```

## 6. RViz에서 목표 주기

- **Nav2 Goal** 버튼으로 맵 위 원하는 위치를 클릭하면, 그 좌표로 자동 주행합니다.
- loc용 RViz 설정(`config/rviz_loc.rviz`)에 Nav2 Goal 도구가 포함되어 있어야 합니다.

**예제처럼 AMCL 파티클 구름 보기:**  
`config/rviz_loc.rviz`에 **PoseArray** 디스플레이를 추가해 두었습니다. 이름은 "Amcl Particle Swarm", 토픽은 `/particle_cloud`입니다. AMCL이 떠 있으면 맵 위에 초록/빨간 점들이 모여 있는 것이 파티클 구름입니다. 수동으로 넣으려면 RViz 왼쪽 **Displays** → **Add** → **By display type** → **PoseArray** 선택 후 **Topic**을 `/particle_cloud`로 설정하면 됩니다.

**3번째 사진처럼 맵·경로·costmap 보기 (목표 입력 시):**  
목표를 주면 **전역 경로(초록 선)**가 보이도록 **Path** 디스플레이(토픽 `/plan`, 이름 "Global Plan")를 두었습니다. **costmap**(장애물 주변 보라/파랑 퍼짐)은 **Map** 디스플레이에 **Color Scheme: costmap**으로 보는 방식이며, `config/rviz_loc.rviz`에 **Local Costmap**(토픽 `/local_costmap/costmap`), **Global Costmap**(토픽 `/global_costmap/costmap`)을 이미 넣어 두었습니다. Nav2가 떠 있으면 두 번째 사진처럼 보라색 퍼짐이 보입니다.

**목표 입력 시 "계속 위치 찾다가" 오류 나는 경우:**

| 현상 | 원인·대응 |
|------|-----------|
| **Failed to make progress** / **Goal ABORTED** | 컨트롤러가 “진행 못 함”으로 판단해 중단. (1) **초기 위치**가 실제와 맞는지 RViz **2D Pose Estimate**로 다시 찍기. (2) 목표가 **장애물 안**이거나 막혀 있지 않은지 확인. (3) `ros2 topic echo /cmd_vel`로 목표 보낸 뒤 **속도가 나가는지** 확인. 나가면 Webots가 받는지, 안 나가면 Nav2 쪽 확인. (4) **AMCL**이 수렴했는지 확인(파티클이 한곳에 모여 있는지). |
| **Control loop missed its desired rate (20Hz vs 13Hz)** | 제어 루프가 20Hz를 못 맞춤. 주파수는 model_dt 때문에 20으로 유지해야 해서, **경고만** 나올 수 있음. CPU 여유 있으면 다른 노드 줄이거나, 이 경고는 무시하고 진행 가능. |
| **lidar_link: timestamp earlier than transform cache** | 라이다 메시지 시각이 TF 캐시보다 과거. `use_sim_time` 미사용이면 시각은 모두 wall clock. 로봇 컨트롤러가 **TF를 먼저** 내보낸 뒤 스캔을 내보내는지 확인. 한울은 같은 노드에서 TF·스캔을 같이 보내므로 보통 문제 없음. 심하면 **초기 위치를 다시 주고** AMCL이 수렴한 뒤에만 목표를 주기. |
| **/particle_cloud has more than one types (PoseArray, ParticleCloud)** | 같은 토픽에 두 메시지 타입이 붙어 RViz가 경고함. **PoseArray** 디스플레이만 쓰면 geometry_msgs/PoseArray만 보면 됨. nav2_rviz_plugins의 ParticleCloud 디스플레이를 쓸 경우 한 타입만 구독되므로, 둘 중 하나만 켜 두면 됨. |

## 7. 설정 파일

- **config/nav2_params.yaml**: Nav2 전용 파라미터 (costmap, controller, planner, velocity_smoother 등).
- 한울은 옴니휠이므로 `velocity_smoother`에서 `linear.y`(좌우 속도)를 허용하도록 설정되어 있습니다.
- `robot_base_frame`은 `base_footprint`로 맞춰져 있습니다.

### 6.1 위험 구역·안전 관련 설정 (현재 값과 이유)

**① collision_monitor (즉각 위험 구역 – 폴리곤)**

| 항목 | 값 | 이유 |
|------|-----|------|
| `enabled` | `False` | 도킹/네비만 쓰는 단계에서는 즉각 정지 구역을 쓰지 않음. 노드는 lifecycle에 포함돼서 **초기화만 되면 됨** → `polygons`·`observation_sources`는 필수로 둠. |
| `polygons` | `["PolygonStop"]` | Nav2가 **polygons 파라미터를 필수**로 요구해서, 초기화만 되도록 **한 개 영역**을 지정. |
| `PolygonStop` | `type: polygon`, `points: [[0.3,0.2],[0.3,-0.2],[0.0,-0.2],[0.0,0.2]]` | 로봇 **앞쪽 0.3m×0.4m 사각형** (base_footprint 기준). `enabled: True`일 때 이 안에 장애물이 `min_points: 4` 이상 들어오면 **정지**(`action_type: stop`). |
| `min_points` | `4` | 위 폴리곤 안에 장애물 점이 4개 이상일 때만 정지. (Jazzy 등에서 요구하는 최소 개수.) |
| `visualize` | `False` | RViz에 폴리곤 안 그려도 됨. |
| `observation_sources` / `scan` | `["scan"]`, `type: "scan"`, `topic: "scan"` | collision_monitor가 **라이다 스캔**으로 장애물을 보도록 함. 이게 없으면 노드 초기화 실패. |
| `cmd_vel_in_topic` / `cmd_vel_out_topic` | `cmd_vel_smoothed` → `cmd_vel` | velocity_smoother 출력을 받아서, 위험 시에만 제한한 뒤 **최종 cmd_vel**로 내보냄. |

**② costmap (장애물·위험 퍼짐)**

| 항목 | 값 | 이유 |
|------|-----|------|
| `robot_radius` (local/global) | `0.22` | 한울 로봇을 **원으로 근사했을 때 반지름**(m). 이만큼은 로봇 본체로 간주해 장애물과 겹치지 않게 함. |
| `inflation_layer` / `inflation_radius` | `0.70` | 장애물 주변 **0.7m**까지 비용이 퍼짐. 이 구역을 “위험 구역”처럼 써서 경로가 장애물에서 멀리 지나가게 함. |
| `inflation_layer` / `cost_scaling_factor` | `3.0` | 퍼지는 비용이 거리에 따라 얼마나 빨리 줄어들지. 클수록 “살짝만 떨어져도 비용 감소” → 경로가 장애물에 조금 더 가깝게 갈 수 있음. |
| `voxel_layer`(local) / `obstacle_layer`(global) | `observation_sources: scan`, `/scan` | 라이다로 **장애물 표시·제거**(marking/clearing). 이 레이어들이 “여기 막혀 있다”는 정보를 주고, 위 `inflation_layer`가 그 주변을 위험 구역으로 넓힘. |

**③ velocity_smoother (속도·가속 제한)**

| 항목 | 값 | 이유 |
|------|-----|------|
| `max_velocity` | `[0.5, 0.5, 2.0]` | **vx, vy, omega** 상한(m/s, m/s, rad/s). 옴니휠이라 **vy도 0.5**로 둠. |
| `min_velocity` | `[-0.5, -0.5, -2.0]` | 후진·옆진·역회전 하한. 대칭으로 둠. |
| `max_accel` / `max_decel` | `[2.5, 2.5, 3.2]` / `[-2.5, -2.5, -3.2]` | 가속·감속 한도. 갑자기 튀지 않게, 모터/구동에도 무리 없게 선택. |

**④ controller_server (진행·목표·속도)**

| 항목 | 값 | 이유 |
|------|-----|------|
| `controller_frequency` | `20.0` | MPPI의 **model_dt(0.05초)**와 맞추기 위해. 15Hz로 낮추면 “Controller period more then model dt” 에러 나서 **20Hz 유지**. |
| `progress_checker` / `required_movement_radius` | `0.15` | **0.15m**만 움직여도 “진행했다”고 인정. 원래 0.5m는 짧은 구간에서 너무 빡세서 “Failed to make progress”가 잘 났음. |
| `progress_checker` / `movement_time_allowance` | `20.0` | 위 0.15m를 **20초 안에** 하면 통과. 천천히 가도 포기하지 않도록 완화. |
| `general_goal_checker` / `xy_goal_tolerance` | `0.25` | 목표 지점 반경 **0.25m** 안이면 도착 처리. |
| `FollowPath`(MPPI) / `motion_model` | `"Omni"` | 한울은 **옴니휠**이라 옆 이동(vy) 필요. `DiffDrive`면 vy를 안 써서 진행 실패로 중단됨 → **Omni**로 설정. |
| `vx_max/min`, `vy_max/min`, `wz_max` | 0.5/-0.35, 0.5/-0.5, 1.9 | planner/controller가 내는 속도 범위. velocity_smoother 상한과 맞춤. |

**요약**:  
- **폴리곤** = collision_monitor가 쓰는 **“즉각 정지할 사각형 영역”** 하나(PolygonStop)만 넣어 둔 것이고, **enabled: False**라 실제 동작은 안 함.  
- **진짜 위험 구역**은 costmap의 **inflation_radius(0.7m)** + **robot_radius(0.22)** 로, 장애물 주변을 넓게 “위험”으로 쳐서 경로가 피해 가게 되어 있음.  
- 방금 수정한 옵션(**progress_checker 완화**, **motion_model: Omni**, **controller_frequency 20 유지**)도 위 표에 반영됨.

## 8. Nav2 문서에서 참고할 곳

[Navigation Plugins (docs.nav2.org)](https://docs.nav2.org/plugins/index.html)에서 한울(옴니휠) 설정 시 참고할 항목:

- **Controllers**: 옴니/홀로노믹 지원 플러그인 — **DWB Controller**, **TEB Controller**, **MPPI Controller**, **Graceful Controller**, **Rotation Shim Controller**. 한울은 `nav2_params.yaml`에서 controller_plugins로 사용 중인 것을 그대로 쓰면 됨.
- **Costmap Layers**: 라이다 → costmap 반영은 **Obstacle Layer**(2D laser scan + raycasting). 맵과 라이다 일치가 느리면 **AMCL**(로컬라이제이션)과 **update_min_d / update_min_a**가 우선 원인.
- **Y 이동 시 맵/라이다 일치 느림**: AMCL이 **OmniMotionModel**인지 확인. 로컬 터미널용 AMCL은 `start_hanul.sh`에서 `ros2 run nav2_amcl amcl`로 띄우므로, `update_min_d`·`update_min_a`를 이미 0.02로 줄여 둠. 여전히 느리면 `nav2_params.yaml`의 amcl 블록은 Nav2 터미널용이므로, 로컬 터미널 AMCL에는 `-p update_min_d:=0.01 -p update_min_a:=0.01`처럼 추가로 넘겨서 더 자주 갱신할 수 있음.
- **Collision Monitor**: [Using Collision Monitor](https://docs.nav2.org/tutorials/docs/using_collision_monitor.html) — `observation_sources`와 `scan` 설정이 필수. 미설정 시 노드 초기화 실패로 Nav2 bringup 전체가 중단됨.

## 9. 문제 발생 시

- **목표를 보냈는데 "Waiting for an action server..."에서만 대기** / **Nav2 터미널에 "Failed to bring up all requested nodes"**: Nav2 **lifecycle**이 어떤 노드에서 실패한 상태입니다. **Nav2** 탭 로그를 보고:
  - `parameter 'observation_sources' is not initialized` / `Failed to change state for node: collision_monitor` → `collision_monitor`에 `observation_sources`와 `scan` 설정 추가.
  - `parameter 'polygons' is not initialized` → `collision_monitor`에 `polygons`(및 PolygonStop 등) 추가. (여기서 말하는 polygon은 **YAML의 collision_monitor용 영역 설정**이지, 로봇 proto/3D 모델의 polygon이 아님.)
  - `Charging dock plugins not given` / `Failed to change state for node: docking_server` → `docking_server`에 `dock_plugins`와 `docks` 최소 설정 추가. 도킹을 쓰지 않아도 lifecycle에 포함되므로 YAML에 블록이 필요함.
  - `Controller period more then model dt` / `Failed to change state for node: controller_server` → MPPI 컨트롤러는 **제어 주기(1/controller_frequency)**가 **model_dt 이하**여야 함. `controller_frequency: 20.0`이면 주기 0.05초, `model_dt: 0.05`와 같아서 통과. 15Hz로 낮추면 주기 0.067초 > 0.05라 에러 나므로 **20Hz 유지**.
- **목표를 보냈는데 액션은 있는데 로봇이 안 움직임**: 위 collision_monitor 등으로 bringup이 중단되면, 액션 서버는 일부만 떠 있을 수 있어 실제 제어는 동작하지 않습니다. Nav2 탭을 켜고 에러 없이 올라왔는지 확인한 뒤, 다시 목표를 보내세요.
- **nav2_bringup을 찾을 수 없음**: 위 1번대로 `ros-jazzy-nav2-bringup` 설치.
- **목표를 보냈는데 안 감** / **"Failed to make progress"·follow_path Aborting**: (1) 한울은 옴니휠이므로 controller의 **motion_model**이 반드시 **"Omni"**여야 함. "DiffDrive"면 옆으로 못 가서 진행 실패로 중단될 수 있음. (2) **progress_checker**의 `required_movement_radius`를 너무 크게 두면(예: 0.5m) 짧은 거리에서 "진행 실패"로 잘못 판단할 수 있음. `required_movement_radius: 0.15`, `movement_time_allowance: 20.0` 정도로 완화해 둠. (3) RViz에서 로봇 위치(AMCL pose)가 맞는지, `/cmd_vel`이 나가는지 확인.
- **장애물 회피가 너무 공격적/미약**: `config/nav2_params.yaml`의 `inflation_radius`, `cost_scaling_factor`, `robot_radius` 등을 조정.
- **라이다가 인식하는 맵과 저장된 맵이 어긋남 / 업데이트가 느림**
  - **원인**: AMCL 위치 추정이 느리거나 틀려서, costmap·스캔이 맵 위에 잘못 그려짐.
  - **설정**: `nav2_params.yaml`의 `amcl`에서 `update_min_d`, `update_min_a`를 작게 하면 스캔 매칭이 더 자주 돼서 추정이 빨라짐. (현재 0.01 / 0.01 적용됨.)
  - **초기 위치**: RViz **2D Pose Estimate**로 로봇이 실제로 서 있는 곳을 정확히 찍어 주면 AMCL이 수렴하기 쉬움.
  - **재시작**: 초기 위치가 많이 틀렸다면 loc(bringup)을 한 번 끄고, 2D Pose Estimate로 위치 준 뒤 다시 확인.
- **Y 방향(스트래이프)·대각선 이동 시 맵이 전혀 안 움직임 (odom은 변하는데 map 기준 위치만 안 변함)**
  - **확인**: `ros2 topic echo /amcl_pose --once` 로 Y 이동 전후 pose가 바뀌는지 확인. 바뀌지 않으면 AMCL이 map 보정을 안 내보내는 것.
  - **설정**: `robot_model_type`이 반드시 `nav2_amcl::OmniMotionModel`인지 확인. Differential이면 Y 이동 시 추정이 틀어짐.
  - **파라미터**: `alpha5`를 0.25 등으로 약간 올리면 옆 이동(vy) 불확실성을 더 반영해, 파티클이 Y 방향으로 더 퍼져서 수렴할 여지가 생김.
  - **초기 위치**: Y만 많이 움직인 뒤에는 초기 위치가 틀어졌을 수 있음. 2D Pose Estimate로 다시 찍어 주고, 전진/회전을 조금 한 뒤 스트래이프를 쓰면 더 안정적일 수 있음.
- **/amcl_pose가 발행되지 않음 / 맵 갱신이 안 됨**
  - **원인**: AMCL은 기본값으로 `/initialpose`를 받기 전까지 포즈를 발행하지 않음. Init Pose 타이밍이 어긋나면 한 번도 안 나올 수 있음. 또는 `tf_broadcast: false`이면 map→odom을 안 보냄.
  - **nav2_params.yaml 조치**: `set_initial_pose: true`와 `initial_pose: {x,y,z,yaw}`를 넣어 두면, 맵만 받으면 (0,0,0)으로 바로 시작해 `/amcl_pose`와 map→odom을 발행함. 필요 시 RViz **2D Pose Estimate**로 보정.
  - **기타**: `map_topic: "map"`, `scan_topic: "scan"`(공식과 동일), `tf_broadcast: true`, `transform_tolerance: 0.5`, `first_map_only: true` 로 맞춰 두었음.
  - **Y 방향 반대**: J(왼쪽)인데 RViz에서 오른쪽으로 보이면 odom y 부호 문제. `hanul_tf_converter.py`에서 odom TF의 y를 `-y`로 보정해 둠.

## 10. 용어: DiffDrive / Polygon

- **DiffDrive (차동 구동)**: 앞뒤로만 갈 수 있고, 방향은 제자리에서 돌려서 바꾸는 방식. 자동차처럼 **옆으로는 못 감**(vy 없음). Nav2에서 `motion_model: "DiffDrive"`면 전진·후진·회전(vx, omega)만 쓰고, **옴니휠 로봇**은 옆으로도 가야 하므로 `motion_model: "Omni"`로 두어야 함.
- **Polygon (여기서 말하는 것)**: 로봇 3D 모델이나 proto의 “폴리곤”이 아님. Nav2 **collision_monitor** 설정에서 쓰는 **“위험 구역” 모양**을 말함. 로봇 앞(또는 옆)에 **사각형 같은 영역**을 하나 정해 두고, 그 안에 장애물이 들어오면 감속/정지하는데, 그 **영역 이름과 꼭짓점 좌표**를 YAML의 `polygons`, `PolygonStop` 같은 항목으로 적는 것. 그래서 “polygon이 없다” = **YAML에 collision_monitor용 polygons(영역 목록) 설정이 없다**는 뜻임.
