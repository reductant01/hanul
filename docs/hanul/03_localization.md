# 3. 로컬라이제이션 (Localization)

---

## 1. Y 이동 시 맵·라이다 안 맞음 / AMCL이 Y에서 동작 안 함

**오류:** Y축(옆) 이동 시 맵과 라이다가 어긋나거나 AMCL이 Y 방향을 제대로 반영하지 않음.

**이유:** AMCL이 옴니휠용 설정(OmniMotionModel)을 쓰지 않아 기본 모션 모델로만 동작함.

**수정:** `scripts/hanul/hanul_webots.sh`(및 hanul_terminator.sh)에서 `--params-file .../config/hanul/amcl_params.yaml` 사용해 AMCL이 **config/hanul/amcl_params.yaml** 전체를 쓰도록 함.

---

## 2. 맵·라이다·TF 전혀 안 맞음 (Y 이동 시 심함)

**오류:** 맵과 라이다·TF가 크게 어긋나고, Y 방향 이동 시 특히 틀어짐.

**이유:** robot_model_type이 OmniMotionModel이 아니거나, odom의 y 방향/크기가 잘못됨.

**수정:** `ros2 param get /amcl robot_model_type`으로 OmniMotionModel인지 확인. odom y가 틀리면 `common/omni_odometry.py`에서 **delta_y 부호**·**odom_scale_y** 보정. 초기 위치를 2D Pose Estimate로 정확히 설정.

---

## 3. extrapolation into the future (초기 포즈)

**오류:** 초기 포즈 설정 시 "미래로 외삽" 경고.

**이유:** Webots·컨트롤러가 아직 올라오기 전에 2D Pose Estimate나 Init Pose를 먼저 줘서 odom TF가 없음.

**수정:** Webots·컨트롤러를 먼저 켠 뒤, 몇 초 후에 2D Pose Estimate 또는 Init Pose 실행.

---

## 4. /amcl_pose 안 나옴 / 맵 갱신 안 됨

**오류:** AMCL pose가 발행되지 않거나 맵이 갱신되지 않음.

**이유:** 초기 위치를 한 번도 주지 않아 AMCL이 맵 위에서 위치를 추정하지 못함.

**수정:** amcl_params에 `set_initial_pose: true`, `initial_pose` 설정. RViz에서 2D Pose Estimate로 한 번 초기 위치 지정.

---

## 5. 회전 시 AMCL 갱신이 느림

**오류:** 로봇 회전 시 AMCL이 느리게 따라옴.

**이유:** `update_min_a`가 커서 회전 시 업데이트 조건을 채우기까지 시간이 걸림.

**수정:** `config/hanul/amcl_params.yaml`에서 **update_min_a** 줄이기(예: 0.02). 회전이 너무 빠르면 텔레오프 turn 낮추기.

---

## 6. 빠른 회전 시 AMCL 불안정

**오류:** 빠르게 회전하면 AMCL이 불안정해짐.

**이유:** delta_theta 스케일이 틀리거나 회전 속도가 너무 커서 odom과 맵이 어긋남.

**수정:** 회전 속도 낮추기. **delta_theta** 검증(제자리 한 바퀴 후 yaw 약 360°) 후 `common/omni_odometry.py`에서 스케일 보정.

---

## 7. particle_cloud 타입 경고

**오류:** RViz에서 particle_cloud 관련 타입 경고.

**이유:** RViz에 잘못된 디스플레이 타입으로 추가했거나 토픽 타입이 맞지 않음.

**수정:** PoseArray 디스플레이만 사용(Amcl Particle Swarm, `/particle_cloud`).

---

[이전: 2. 맵핑](02_mapping.md) · [다음: 4. 네비게이션](04_navigation.md)
