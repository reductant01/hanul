# 4. 네비게이션 (Navigation)

---

## 1. observation_sources / polygons / dock_plugins 미초기화

**오류:** nav2_params.yaml 관련해 observation_sources, polygons, dock_plugins 미초기화 오류.

**수정:** nav2_params.yaml에 collision_monitor용 observation_sources·polygons, docking_server용 dock_plugins·docks 최소 설정 추가.

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

[이전: 3. 로컬라이제이션](03_localization.md) · [다음: 5. NUC 실제 로봇](05_nuc.md)
