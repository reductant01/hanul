# RViz / AMCL lidar_link 오류 정리

## 1. 나타나는 현상

- **RViz:** `Message Filter dropping message: frame 'lidar_link' at time T for reason 'the timestamp on the message is earlier than all the data in the transform cache'`
- **RViz:** `Message Filter dropping message: frame 'lidar_link' ... for reason 'discarding message because the queue is full'`
- **AMCL:** 동일한 `lidar_link` / `timestamp ... earlier than ... transform cache` 메시지
- Local / Global costmap이 안 나오거나 갱신이 안 됨

## 2. 원인 후보 (가설)

| 후보 | 설명 |
|------|------|
| **A. 스캔 vs map→odom 도착 순서** | 스캔(시각 T)이 RViz/AMCL에 먼저 도착하고, AMCL이 만든 map→odom은 T+δ에 도착. 그래서 시각 T로 TF 조회 시 해당 시각의 map→odom이 캐시에 없음. |
| **B. RViz 기동이 느림** | 터미네이터로 여러 노드가 동시에 뜨는데, RViz가 늦게 뜨거나 초기화가 느려서, 처음부터 메시지가 쌓이고 TF 캐시가 뒤쳐짐. |
| **C. use_sim_time vs wall clock** | 시뮬에서는 use_sim_time true + /clock을 쓰다가 false로 바꾸는 등 혼용 시, 노드마다 시간 기준이 달라 TF/스탬프가 어긋남. |
| **D. 발행량 vs 처리량** | 스캔/TF 발행 주기가 빠른데, RViz/AMCL 쪽 메시지 필터가 TF 조회 실패를 반복하면 처리 못 한 메시지가 쌓여 queue full 발생. |

어느 하나만이 아니라 A+B, A+D처럼 겹쳐 있을 수 있음.

## 3. TF 체인 (lidar 쪽)

- **map → odom:** AMCL이 발행 (스캔 처리 후)
- **odom → base_footprint:** Webots 컨트롤러가 발행 (오도메트리)
- **base_footprint → lidar_link:** Webots 컨트롤러가 발행 (고정 오프셋)

LaserScan의 `header.frame_id`는 `lidar_link`. RViz/AMCL은 고정 프레임(map)에서 `lidar_link`까지 위 체인으로 변환해 스캔을 그림/처리함.

## 4. 해결 시도했던 것 (효과 미비·복구함)

- use_sim_time true → false 전환
- Webots에서 /clock 발행, 스탬프를 sim_time 또는 sim_time+offset으로 통일
- 스캔 1스텝 지연 발행 (과거 스탬프가 되어 오히려 악화)
- 스캔 80ms 지연 후 stamp=now()로 발행
- 스캔 즉시 1회 + 120ms 후 동일 메시지 재발행
- RViz LaserScan Queue Size / Tolerance / Frame Rate 조정
- AMCL transform_tolerance 증가
- Nav2/RViz 기동 지연 (sleep)

위 수정들은 Webots 컨트롤러에서 제거해 원상 복구한 상태.

## 5. TF 프레임이 나오는 위치 (문제 지점)

| TF 구간 | 발행하는 쪽 | 파일/노드 | 스탬프 | 사진 비유 |
|---------|-------------|-----------|--------|-----------|
| **map → odom** | AMCL | Nav2 `nav2_amcl` | 스캔 처리 **후** 발행 → 스캔 시각보다 **늦은 시각** | 사진의 "tf_odom↔base_link를 100ms 뒤에 발행"과 유사. **여기서 지연 발생.** |
| **odom → base_footprint** | Webots 컨트롤러 | `hanul_controller_webots.py` → `tf_converter.create_odometry_transform` | 매 스텝 `get_clock().now()` | “지금” 시각으로 발행 → 지연 없음 |
| **base_footprint → lidar_link** | Webots 컨트롤러 | `hanul_controller_webots.py` → `tf_converter.create_lidar_transform` | 위와 동일 스탬프 | “지금” 시각으로 발행 → 지연 없음 |

**LaserScan**  
- `header.frame_id = 'lidar_link'`, `header.stamp` = 위와 같은 스탬프 (Webots 컨트롤러에서 생성).

**정리:**  
- **우리 코드에서 “문제가 나는 위치”는 map→odom을 발행하는 AMCL 쪽.**  
- 우리가 직접 고칠 수 있는 건 Webots 쪽(odom→base_footprint, base_footprint→lidar_link)뿐이고, 이 둘은 매 스텝 같은 스탬프로 바로 발행하고 있어서, 사진에서 말하는 “TF를 늦게 보내는 구조”에 해당하지 않음.  
- RViz/AMCL이 스캔 시각 T로 `map → lidar_link`를 조회할 때, **map→odom만** T 시각이 아직 없어서(AMCL이 T+δ에 발행) “timestamp earlier than transform cache”가 나는 것.

## 6. 다음에 확인할 것

- RViz를 **다른 노드보다 훨씬 나중에** (예: 맵/AMCL/Nav2 안정화 후 30초 뒤) 단독으로 실행했을 때도 같은 오류가 나는지 → B(기동 순서/느린 기동) 검증
- `ros2 run tf2_ros tf2_echo map lidar_link` 로 map→lidar_link가 주기적으로 나오는지, 스탬프가 어디서 끊기는지 확인
- AMCL이 map→odom을 **스캔 시각으로** 찍는지, **발행 시각(now())**으로 찍는지 (Nav2 AMCL 소스/파라미터 확인)
