# 1. 로봇 이동 (Robot Movement)

---

## 1. ModuleNotFoundError: No module named 'rclpy' (Webots 컨트롤러 시작 시)

**오류:** Webots 컨트롤러 시작 시 `rclpy`를 찾을 수 없음.

**수정:** (1) Webots를 `./scripts/hanul/hanul_webots.sh map` 또는 `loc`으로 실행. (2) 터미널에 Python 가상환경(.venv)이 켜져 있으면 `deactivate` 후 스크립트 실행. (3) `source /opt/ros/jazzy/setup.bash` 오타 없이 입력.

---

## 2. lidar_link timestamp earlier than transform cache

**오류:** 라이다 링크 타임스탬프가 TF 캐시보다 이전이라 경고 또는 오류.

**수정:** odom TF와 스캔에 **동일 stamp**를 사용하도록 controller·tf_converter에서 같은 시각 사용.

---

## 3. /cmd_vel이 0.01~0.02 수준으로 너무 작음

**오류:** 텔레오프나 Nav2에서 보낸 속도가 실제로는 거의 안 움직이는 수준으로 들어옴.

**수정:** `common/ros_bridge.py`에서 작은 cmd_vel에 대한 스케일업 옵션 사용.

---

## 4. Y 이동 시 odom y가 실제와 다름(방향/크기)

**오류:** Y축(옆)으로 이동해도 odom의 y 값이 실제 이동과 방향·크기가 맞지 않음.

**수정:** `common/omni_odometry.py`에서 **delta_y 부호** 또는 **odom_scale_y** 보정. [3. 로컬라이제이션](03_localization.md) 참고.

---

## 5. echo_odom_pose.py 실행 시 TF extrapolation

**오류:** 오도메트리 pose를 조회할 때 TF를 미래로 외삽한다는 경고.

**수정:** 스크립트에서 `Time(0,0)`으로 최신 TF를 요청하도록 변경.

---

[다음: 2. 맵핑](02_mapping.md)
