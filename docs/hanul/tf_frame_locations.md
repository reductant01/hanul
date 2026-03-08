# 우리 코드에서 TF 프레임을 다루는 위치

## 1. TF를 발행하는 부분 (프레임 설정 포함)

### common/tf_converter.py
| 줄 | 내용 | frame_id | child_frame_id |
|----|------|----------|----------------|
| 19-20 | `create_odometry_transform` | `odom` | `base_footprint` |
| 37-38 | `create_lidar_transform` | `base_footprint` | `lidar_link` |
| 53-54 | `create_laser_transform` (lidar 복제) | `base_footprint` | `laser` |
| 65 | `create_laser_scan_msg` (LaserScan header) | - | `header.frame_id = 'lidar_link'` |

### common/ros_bridge.py
| 줄 | 내용 |
|----|------|
| 21-22 | `TransformBroadcaster`, `StaticTransformBroadcaster` 생성 |
| 50-52 | `publish_transform()` → `tf_broadcaster.sendTransform(transform_msg)` |

### controllers/hanul_controller_webots/hanul_controller_webots.py
| 줄 | 내용 | 발행하는 TF |
|----|------|--------------|
| 48-51 | odom TF 생성 후 발행 | odom → base_footprint |
| 52-53 | lidar TF 생성 후 발행 | base_footprint → lidar_link |
| 56-65 | LaserScan 생성 (frame_id lidar_link) | - |

### controllers/hanul_controller_nuc/hanul_controller_nuc.py
| 줄 | 내용 | 발행하는 TF |
|----|------|--------------|
| 36-39 | odom TF 생성 후 발행 | odom → base_footprint |
| 40-43 | lidar + laser TF 발행 | base_footprint → lidar_link, base_footprint → laser |
| 45-54 | LaserScan 생성 (frame_id lidar_link) | - |

---

## 2. 설정 파일에서 프레임 이름을 쓰는 부분

### config/hanul/amcl_params.yaml
- `base_frame_id: "base_footprint"`
- `global_frame_id: "map"`
- `odom_frame_id: "odom"`

### config/hanul/nav2_params.yaml
- AMCL: `base_frame_id`, `global_frame_id`, `odom_frame_id` (위와 동일)
- bt_navigator: `global_frame: map`, `robot_base_frame: base_footprint`
- costmap: `global_frame` (odom 또는 map), `robot_base_frame: base_footprint`
- 기타: `base_frame_id`, `odom_frame_id`, `fixed_frame`, `frame` 등

### config/hanul/rviz_loc.rviz
- `Fixed Frame: map`

---

## 3. 메시지 header.frame_id만 설정하는 부분

### scripts/amcl_pose_estimate.py (94줄)
- `msg.header.frame_id = "map"` (PoseWithCovarianceStamped, /initialpose)

### scripts/go_to_map_origin.py (39줄)
- `goal_msg.pose.header.frame_id = "map"` (PoseStamped, navigate_to_pose)

---

## 4. TF 프레임 “문제”가 우리 코드에서 나오는지 여부

- **프레임 이름**: 위 위치들에서 모두 `map`, `odom`, `base_footprint`, `lidar_link`를 일관되게 사용함. 오타나 불일치 없음.
- **체인**: map(AMCL) → odom(AMCL) → base_footprint(우리) → lidar_link(우리). 우리가 발행하는 구간(odom→base_footprint→lidar_link)은 올바름.
- **실제 오류 원인**: RViz/AMCL의 “timestamp earlier than transform cache”는 **map→odom을 AMCL이 스캔 시각보다 늦게 발행**하는 타이밍 문제이며, **우리 코드의 프레임 이름/설정이 잘못된 부분은 없음.**

요약: **우리 코드에서 TF 프레임 “문제”가 발생하는 위치는 없고**, 문제는 AMCL의 map→odom 발행 시각에 있음.
