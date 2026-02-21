# 맵 파일 만들기 (YAML + PGM)

## 요약: 직접 만들지 않음

**YAML과 PGM은 손으로 만들지 않습니다.**  
맵핑(SLAM)으로 만든 맵을 **저장 명령 한 번**으로 두 파일이 함께 생성됩니다.

---

## 1. 맵 만드는 순서

### Step 1: 맵핑 (지금처럼)
1. `start_hanul.sh` 로 Webots + SLAM Toolbox + RViz 실행
2. 로봇을 움직여서 맵이 잘 쌓이게 함
3. 맵이 충분히 넓어지면 다음 단계로

### Step 2: 맵 저장 (한 번에 YAML + PGM 생성)
터미널에서 **ROS 2 환경**을 연 뒤:

```bash
source /opt/ros/jazzy/setup.bash
cd /mnt/hanul
ros2 run nav2_map_server map_saver_cli -f maps/hanul_map
```

- `-f maps/hanul_map` : 저장할 파일 이름(확장자 없이)
- 실행하면 **같은 폴더에** 다음 두 파일이 생깁니다:
  - `maps/hanul_map.yaml`
  - `maps/hanul_map.pgm` (또는 `hanul_map.png`)

이때 **SLAM Toolbox와 Webots가 켜져 있어야** `/map` 토픽이 있으므로, **맵핑 중인 상태에서** 다른 터미널을 열어 위 명령만 실행하면 됩니다.

---

## 2. 생성되는 YAML 파일 내용

`map_saver_cli`가 자동으로 만드는 YAML 예시는 아래와 비슷합니다.

```yaml
image: hanul_map.pgm
resolution: 0.05
origin: [-3.0, -2.0, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
```

| 항목 | 의미 |
|------|------|
| **image** | 같은 폴더에 있는 이미지 파일 이름 (.pgm 또는 .png) |
| **resolution** | 셀 1개당 미터 (SLAM 해상도와 맞추기, 보통 0.05) |
| **origin** | 맵 원점의 [x, y, yaw] (미터, 라디안) |
| **negate** | 0=흰색이 빈 공간, 1=반전 |
| **occupied_thresh** | 이 값 이상이면 장애물로 처리 |
| **free_thresh** | 이 값 이하면 빈 공간으로 처리 |

**수동으로 고칠 일**이 있으면 이 YAML만 에디터로 열어서 수정하면 됩니다.  
PGM은 이미지 파일이라 **직접 만들거나 수정하지 않습니다.**

---

## 3. PGM 파일은?

- **직접 만들 필요 없음.** `map_saver_cli`가 `/map` 토픽(점유 그리드)을 받아서 **자동으로** PGM(또는 PNG) 이미지로 저장합니다.
- 형식: 흰색=빈 공간, 검정=장애물, 회색=미지역.

---

## 4. 정리

| 하고 싶은 일 | 방법 |
|-------------|------|
| **기존 맵 파일을 만든다** | 맵핑 실행 중에 `map_saver_cli -f maps/hanul_map` 실행 → `hanul_map.yaml` + `hanul_map.pgm` 생성 |
| **YAML만 고친다** | 생성된 `maps/hanul_map.yaml` 을 에디터로 열어서 수정 |
| **PGM을 만든다** | 별도로 만들지 않음. 항상 `map_saver_cli`로 YAML과 함께 생성 |

**한 번에 할 일:** 맵핑 끝난 뒤 `ros2 run nav2_map_server map_saver_cli -f maps/hanul_map` 한 번 실행하면, `maps/` 안에 YAML과 PGM이 함께 생깁니다.
