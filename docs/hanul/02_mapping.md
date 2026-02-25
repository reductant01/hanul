# 2. 맵핑 (Mapping)

이 문서는 **맵핑 단계**에서 겪은 오류와 해결방법을 정리한 것입니다.

---

## 개요

맵 없이 SLAM으로 맵을 만들고 저장하는 방법입니다.

---

## 실행

1. `cd /mnt/hanul` → `./scripts/hanul/hanul_webots.sh map`
2. Webots + SLAM Toolbox + RViz 확인 후, Teleop으로 주행하며 맵 생성
3. 저장: `ros2 run nav2_map_server map_saver_cli -f maps/hanul/저장이름` → `maps/hanul/저장이름.yaml`, `.pgm` 생성 (한울 맵은 `maps/hanul/`에 저장)

**설정**: `config/slam_toolbox_params.yaml` (map), `config/amcl_params.yaml` (loc), `config/nav2_params.yaml` (loc·Nav2), `config/rviz_map.rviz`. loc에서 쓸 맵은 `scripts/hanul/hanul_terminator.sh`의 MAP_YAML(`maps/hanul/hanul_map.yaml`)과 맞추면 됩니다.

---

## 오류 → 대응

맵핑 단계에서 겪은 오류가 있으면 아래 표에 추가.

| 현상 | 대응 |
|------|------|
| (예: SLAM 맵이 깨짐) | (해결 방법) |

---

[이전: 1. 로봇 이동](01_robot_movement.md) · [다음: 3. 로컬라이제이션](03_localization.md)
