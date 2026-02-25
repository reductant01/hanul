# 1. 로봇 이동 (Robot Movement)

Webots 한울 로봇이 `/cmd_vel`로 구동되고, 오도메트리·TF·`/scan`을 발행하는 구조입니다.

---

## 구조 요약

- **Webots** `worlds/hanul.wbt` → 한울 컨트롤러(`controllers/hanul_controller/`)가 매 스텝: `/cmd_vel` 구독 → 역기구학 → 모터, 엔코더 → 오도메트리 → odom→base_footprint TF, 라이다 → `/scan`·lidar_link TF.
- **주요 파일**: `hanul_controller.py`(메인), `hanul_ros_bridge.py`(cmd_vel/scan/TF), `hanul_webots.py`(모터·센서), `hanul_inverse_kinematics.py`, `hanul_odometry.py`, `hanul_tf_converter.py`.

---

## 오류 → 대응

| 현상 | 대응 |
|------|------|
| `lidar_link timestamp earlier than transform cache` | odom TF와 스캔에 **동일 stamp** 사용 (controller·tf_converter). |
| `/cmd_vel`이 0.01~0.02 수준으로 너무 작음 | `hanul_ros_bridge.py` 작은 cmd_vel 스케일업 옵션. AMCL·costmap 안정화 후에도 확인. |
| Y 이동 시 odom y가 실제와 다름(방향/크기) | `hanul_odometry.py`의 **delta_y 부호** 또는 **odom_scale_y** 보정. [3. 로컬라이제이션](03_localization.md) 참고. |
| `echo_odom_pose.py` 실행 시 TF extrapolation | 스크립트에서 `Time(0,0)`으로 최신 TF 요청. |

---

## 확인

- Webots만: `source /opt/ros/jazzy/setup.bash` 후 `webots worlds/hanul.wbt`
- 오도메트리 Y: 텔레오프로 Y 이동 후 `python3 scripts/echo_odom_pose.py --once` 로 y 변화량 확인.

---

[다음: 2. 맵핑](02_mapping.md) · [목차: nav2_usage](nav2_usage.md)
