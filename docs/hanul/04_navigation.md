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

**이유:** RViz에 PoseArray 디스플레이를 추가하지 않았거나, 토픽을 `/particle_cloud`로 지정하지 않음. AMCL은 초기 위치를 받은 뒤에야 파티클을 발행함.

**수정:** RViz에서 **By topic** 또는 **By display type**으로 **PoseArray** 디스플레이 추가 후 토픽을 `/particle_cloud`로 지정. 초기 위치(2D Pose Estimate 또는 amcl_pose_estimate.py)를 한 번 준 뒤에는 파티클이 발행됨. 타입은 PoseArray만 사용.

---

## 6. Nav2 패널에서 Localization / Navigation이 inactive

**오류:** 로컬라이제이션·네비게이션은 동작하는데 Nav2 패널에 Localization 또는 Navigation이 inactive로만 표시됨.

**이유:** 패널은 **노드 이름**이 `lifecycle_manager_localization`(로컬라이제이션), `lifecycle_manager_navigation`(네비게이션)인 lifecycle 매니저만 인식함. 이름이 다르면 실제로는 동작해도 inactive로만 보임.

**수정:** map_server·amcl을 관리하는 lifecycle 매니저 실행 시 `-r __node:=lifecycle_manager_localization` 추가. (`hanul_webots.sh`에 반영됨.) Navigation은 `navigation_launch.py` 기동이 끝날 때까지 대기하면 active로 바뀜.

---

[이전: 3. 로컬라이제이션](03_localization.md) · [다음: 5. NUC 실제 로봇](05_nuc.md)
