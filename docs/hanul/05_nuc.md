# 5. NUC 실제 로봇 (Real Robot on NUC)

---

## 1. USB 포트가 ttyUSB0/1로 바뀌어서 모터/라이다 구분 어려움

**오류:** 부팅·재연결 순서에 따라 ttyUSB 번호가 바뀌어, 어떤 포트가 모터이고 라이다인지 알기 어려움.

**수정:** udev 규칙으로 장치별 고정 이름 부여. 다이나믹셀 → `/dev/wheel`, 라이다 → `/dev/lidar`. `udevadm info -a -n /dev/ttyUSB1` 등으로 idVendor·idProduct 확인 후 `/etc/udev/rules.d/99-hanul-usb.rules`에 SYMLINK+="wheel", SYMLINK+="lidar" 규칙 추가. `udevadm control --reload-rules`, `udevadm trigger` 후 USB 재연결. 스크립트는 MOTOR_PORT=/dev/wheel, LIDAR_PORT=/dev/lidar 사용.

---

## 2. 키보드(teleop)로 명령해도 바퀴가 안 움직임

**오류:** 텔레오프로 키를 눌러도 바퀴가 반응하지 않음.

**수정:** 다이나믹셀이 Position 모드(3)라 Goal Velocity를 무시함. `hanul_hardware_nuc.py`에서 초기화 시 Operating Mode = 1(Velocity) 설정. Dynamixel Wizard에서도 ID 1·2·3 모두 Velocity로 설정 후 EEPROM 저장·재부팅.

---

## 3. 1번 모터만 움직이고 2·3번은 안 움직임

**오류:** ID 1만 구동되고 ID 2·3은 안 움직임.

**수정:** ID 2·3이 여전히 Position 모드임. Dynamixel Wizard에서 ID 2, ID 3도 Operating Mode = Velocity(1)로 바꾸고 EEPROM 저장, USB 재연결 또는 재부팅.

---

## 4. 맵이 로봇 초기 위치가 아닌 멀리 떨어진 곳에 생성됨

**오류:** map 모드로 실행하면 SLAM 맵이 로봇 시작 위치가 아니라 화면에서 한참 떨어진 곳에 생성됨.

**원인:** (1) 오도메트리가 “이전 엔코더 = 0”으로 두어 첫 프레임에서 (현재 틱 − 0)×R 같은 큰 델타가 나옴. (2) 엔코더 값이 틱(0~4095)인데 라디안으로 변환하지 않아 스케일이 틀림.

**수정:** (1) `common/omni_odometry.py`: 첫 번째 update()에서만 이전 엔코더를 그때 읽은 값으로 두고 델타 0. 이후부터만 델타 누적. (2) `controllers/hanul_controller_nuc/hanul_hardware_nuc.py`: get_encoder_values()에서 틱 → 라디안 변환(틱 × 2π/4095) 후 반환.

---

## 5. 전진(I) 누르면 뒤로 가고 방향이 전부 반대

**오류:** 전진 시 뒤로 가고, 다른 방향도 모두 반대로 동작함.

**수정:** 로봇/모터 배선과 코드 좌표계가 반대. `common/ros_bridge.py`의 cmd_vel_callback에서 `vx=-msg.linear.x`, `vy=msg.linear.y`, `w=-msg.angular.z` 로 부호 반전.

---

## 6. 회전 속도가 평행 이동보다 너무 빠름

**오류:** 직선 이동에 비해 회전이 지나치게 빠름.

**수정:** `common/ros_bridge.py`에 linear_speed_max, angular_speed_max 등 별도 변수 두고 angular_speed_max를 0.5 등으로 낮춤. hanul_terminator.sh에서 teleop 기본 turn도 0.5로 조정.

---

## 7. 멈춤 명령을 줘도 천천히 멈춤

**오류:** 키보드로 멈춤을 눌러도 로봇이 서서히 멈춤.

**수정:** 가속 완화 때문에 목표 0에도 점점 0으로 수렴하던 동작. `common/omni_velocity.py`에서 목표가 모두 0일 때는 현재 속도를 0으로 바로 설정하고 return 하도록 변경. 이동 중 가속 완화는 유지.

---

## 8. RViz "Message Filter dropping message" (lidar_link 타임스탬프) / Local Costmap 오류

**오류:** RViz에서 "Message Filter dropping message: frame 'lidar_link' at time ... the timestamp on the message is earlier than all the data in the transform cache" 경고가 반복되고, Local Costmap 디스플레이에 주황색 느낌표 오류가 뜸. 스캔·TF 타임스탬프 불일치로 메시지가 버려짐.

**수정:** (1) `config/hanul/rviz_map.rviz`, `config/hanul/rviz_loc.rviz`에서 LaserScan 디스플레이의 **Tolerance를 10.0**으로 설정해, 타임스탬프가 TF 캐시보다 조금 오래된 메시지도 표시되도록 함. (2) Local Costmap이 스캔을 수용하도록 `config/hanul/nav2_params.yaml`의 local_costmap → voxel_layer에 **tf_filter_tolerance: 10.0** 추가. (3) global_costmap → obstacle_layer에도 **tf_filter_tolerance: 10.0** 추가.

---

## 9. Webots 옴니휠·스캔·odom 방향이 NUC 실제 로봇과 다름

**오류:** Webots 시뮬레이션에서 옴니휠의 양의 회전 방향이 NUC 실제 로봇과 반대이고, 스캔 각도 순서와 odom 방향이 맞지 않아 시뮬레이션만 다른 동작을 함.

**수정:** NUC와 동일하게 보이도록 Webots 쪽만 수정. (1) **스캔 배열 순서:** `controllers/hanul_controller_webots/hanul_controller_webots.py`에서 라이다 데이터를 `lidar_data['ranges'][::-1]`로 역순하여 LaserScan에 넣음. (2) **odom yaw:** `common/tf_converter.py`의 `create_odometry_transform`에 `yaw_offset` 인자 추가, Webots에서 필요 시 호출 시 `yaw_offset`으로 방향 보정. (3) **vy·vx·w 부호:** Webots에서만 `robot.set_cmd_vel(-vx, -vy, -w)`로 전달해 실제 로봇과 같은 방향으로 구동되도록 함.

---

[이전: 4. 네비게이션](04_navigation.md)
