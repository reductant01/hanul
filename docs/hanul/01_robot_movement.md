# 1. 로봇 이동 (Robot Movement)

이 문서는 **로봇 이동 단계**에서 겪은 오류와 해결방법을 정리한 것입니다.

---

## 개요

Webots 한울 로봇이 `/cmd_vel`로 구동되고, 오도메트리·TF·`/scan`을 발행하는 구조입니다.

---

## 실행 요약

```bash
cd /mnt/hanul
./scripts/hanul/hanul_webots.sh loc   # 저장 맵 + AMCL + Nav2
./scripts/hanul/hanul_webots.sh map   # SLAM 맵핑
./scripts/hanul/hanul_nuc.sh          # 실제 로봇 (NUC)
```

---

## 구조 요약

- **Webots** `worlds/hanul/hanul.wbt` → 컨트롤러 `controllers/hanul_controller_webots/`가 매 스텝: `/cmd_vel` 구독 → 역기구학 → 모터, 엔코더 → 오도메트리 → odom→base_footprint TF, 라이다 → `/scan`·lidar_link TF.
- **실제 로봇 (NUC)** `controllers/hanul_controller_nuc/` 진입점 `hanul_controller_nuc.py`, 하드웨어 `hanul_hardware_nuc.py`.
- **공통**: `common/` — `omni_odometry.py`, `omni_inverse_kinematics.py`, `tf_converter.py`, `ros_bridge.py`.

---

## 오류 → 대응

| 현상 | 대응 |
|------|------|
| `ModuleNotFoundError: No module named 'rclpy'` (Webots 컨트롤러 시작 시) | (1) Webots를 **반드시** `./scripts/hanul/hanul_webots.sh map` 또는 `loc`으로 실행. (2) 터미널에 **Python 가상환경(.venv)** 이 켜져 있으면 끄고 실행(`deactivate` 후 스크립트 실행). 스크립트는 Webots 탭에서 자동으로 venv를 끄고 ROS를 불러오도록 되어 있음. (3) `source /opt/ros/jazzy/setup.bash` 시 **오타 없이** `setup.bash` 로 입력. |
| `lidar_link timestamp earlier than transform cache` | odom TF와 스캔에 **동일 stamp** 사용 (controller·tf_converter). |
| `/cmd_vel`이 0.01~0.02 수준으로 너무 작음 | `common/ros_bridge.py` 작은 cmd_vel 스케일업 옵션. |
| Y 이동 시 odom y가 실제와 다름(방향/크기) | `common/omni_odometry.py`의 **delta_y 부호** 또는 **odom_scale_y** 보정. [3. 로컬라이제이션](03_localization.md) 참고. |
| `echo_odom_pose.py` 실행 시 TF extrapolation | 스크립트에서 `Time(0,0)`으로 최신 TF 요청. |

---

## 확인

- Webots만: `source /opt/ros/jazzy/setup.bash` 후 `webots worlds/hanul/hanul.wbt`
- 오도메트리 Y: 텔레오프로 Y 이동 후 `python3 scripts/echo_odom_pose.py --once` 로 y 변화량 확인.

---

[다음: 2. 맵핑](02_mapping.md)
