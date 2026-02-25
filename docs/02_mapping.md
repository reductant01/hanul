# 2. 맵핑 (Mapping)

맵 없이 SLAM으로 맵을 만들고 저장하는 방법입니다.

---

## 실행

1. `cd /mnt/hanul` → `./start_hanul.sh map`
2. Webots + SLAM Toolbox + RViz 확인 후, Teleop으로 주행하며 맵 생성
3. 저장: `ros2 run nav2_map_server map_saver_cli -f maps/저장이름` → `maps/저장이름.yaml`, `.pgm` 생성

**설정**: `config/slam_toolbox_params.yaml`, `config/rviz_map.rviz`. loc 모드에서 쓸 맵은 `start_hanul.sh`의 `MAP_YAML`이 가리키는 경로와 맞추면 됩니다.

---

[이전: 1. 로봇 이동](01_robot_movement.md) · [다음: 3. 로컬라이제이션](03_localization.md) · [목차: nav2_usage](nav2_usage.md)
