# 3. 로컬라이제이션 (Localization)

이 문서는 **로컬라이제이션 단계**에서 겪은 오류와 해결방법을 정리한 것입니다.

---

## 개요

저장된 맵 위에서 AMCL로 로봇 위치를 추정합니다. `scripts/hanul/hanul_webots.sh loc` 실행 시 AMCL이 **config/amcl_params.yaml**을 사용합니다 (OmniMotionModel, set_initial_pose 등). 초기 위치는 Init Pose 터미널(3초 후 (0,0)) 또는 RViz **2D Pose Estimate**로 설정.

---

## 오류 → 대응

| 현상 | 대응 |
|------|------|
| Y 이동 시 맵·라이다 안 맞음 / AMCL이 Y에서 동작 안 함 | AMCL이 **amcl_params.yaml** 전체를 쓰도록 `scripts/hanul/hanul_webots.sh`(및 scripts/hanul/hanul_terminator.sh)에서 `--params-file .../amcl_params.yaml` 사용. 옴니는 **OmniMotionModel** 필수. |
| 맵·라이다·TF 전혀 안 맞음 (Y 이동 시 심함) | `ros2 param get /amcl robot_model_type` → OmniMotionModel인지 확인. odom y 방향/크기 틀리면 `common/omni_odometry.py` **delta_y 부호**·**odom_scale_y** 보정. 초기 위치를 2D Pose Estimate로 정확히. |
| `extrapolation into the future` (초기 포즈) | Webots·컨트롤러 먼저 켠 뒤, 몇 초 후 2D Pose Estimate 또는 Init Pose. |
| /amcl_pose 안 나옴 / 맵 갱신 안 됨 | amcl_params에 `set_initial_pose: true`, `initial_pose` 있음. 2D Pose Estimate로 한 번 주기. |
| 회전 시 AMCL 갱신이 느림 | `amcl_params.yaml`에서 **update_min_a** 줄이기 (예: 0.02). 회전 속도 너무 빠르면 텔레오프 turn 낮추기. |
| 빠른 회전 시 AMCL 불안정 | 회전 속도 낮추기. 근본은 **delta_theta** 검증(360° 테스트) 후 `common/omni_odometry.py`에서 스케일 보정. |
| particle_cloud 타입 경고 | PoseArray 디스플레이만 사용 (Amcl Particle Swarm, `/particle_cloud`). |

---

## 오도메트리 확인 (Y·회전)

- **Y**: 이동 전·후 `python3 scripts/echo_odom_pose.py --once` → y 변화량·방향이 실제 이동과 맞는지 확인. 틀리면 `common/omni_odometry.py`의 delta_y·odom_scale_y.
- **회전**: 제자리 한 바퀴 후 yaw 변화가 약 360°인지 확인. 틀리면 delta_theta 스케일 보정.

**보정 위치**: `common/omni_odometry.py` (delta_y, delta_theta, odom_scale_x/y).

---

[이전: 2. 맵핑](02_mapping.md) · [다음: 4. 네비게이션](04_navigation.md)
