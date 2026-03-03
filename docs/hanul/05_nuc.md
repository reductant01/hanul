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

## 8. RViz "Message Filter dropping message" (queue full)

**오류:** RViz에서 laser 프레임 메시지가 큐가 가득 차서 버려진다는 경고.

**수정:** `config/rviz_map.rviz`, `config/rviz_loc.rviz`에서 LaserScan의 Topic Depth·Queue Size를 50으로 증가. SLAM 쪽 `config/slam_toolbox_params.yaml`에서 throttle_scans 증가로 발행 속도 완화 가능.

---

[이전: 4. 네비게이션](04_navigation.md)
