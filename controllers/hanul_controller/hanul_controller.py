"""
Hanul 로봇 Webots 컨트롤러 (진입점)

아키텍처:
- hanul_webots.py: 하드웨어 제어 (모터, 센서)
- hanul_inverse_kinematics.py: 역기구학 (명령 → 모터)
- hanul_odometry.py: 오도메트리 계산 (엔코더 → 위치)
- hanul_tf_converter.py: TF 메시지 생성 (계산)
- hanul_ros_bridge.py: ROS 2 통신 (발행/구독만)
- hanul_controller.py: 메인 조율 (이 파일)
"""

import rclpy

from hanul_webots import HanulWebots
from hanul_odometry import HanulOdometry
from hanul_tf_converter import HanulTFConverter
from hanul_ros_bridge import HanulROSBridge, init_ros_node, shutdown_ros_node


class HanulController:
    """메인 컨트롤러: 모든 모듈 조율"""
    
    def __init__(self):
        print("🤖 Hanul Controller Initializing...")
        
        # 1. Webots 시뮬레이터 인터페이스 초기화
        self.webots = HanulWebots()
        print("✅ Webots interface initialized")
        
        # 2. 오도메트리 초기화
        self.odometry = HanulOdometry()
        print("✅ Odometry initialized")
        
        # 3. TF 메시지 변환 모듈 초기화
        self.tf_converter = HanulTFConverter()
        print("✅ TF converter initialized")
        
        # 4. ROS 2 초기화
        init_ros_node()
        self.ros_bridge = HanulROSBridge()
        print("✅ ROS 2 Bridge initialized")
        
        self.running = True
        print("✅ Hanul Controller Ready!\n")
    
    def run(self):
        """메인 시뮬레이션 루프"""
        print("🚀 Starting main loop...")
        print("📡 Waiting for /cmd_vel commands from teleop_twist_keyboard...\n")
        
        step_count = 0
        log_interval = 1000  # 1000 스텝마다 로그 (이전: 10000)
        
        # 라이다는 고정 프레임이므로 정적 TF를 1회만 발행
        t_lidar_static = self.tf_converter.create_lidar_transform(self.ros_bridge)
        self.ros_bridge.publish_static_transform(t_lidar_static)
        
        try:
            while self.webots.step() != -1:
                # 1. ROS 2 콜백 처리
                rclpy.spin_once(self.ros_bridge, timeout_sec=0)
                
                # 2. teleop에서 명령 받기
                vx, vy, w = self.ros_bridge.get_cmd_vel()
                
                # 3. 모터 제어
                self.webots.set_cmd_vel(vx, vy, w)
                
                # 4. 엔코더 읽기 및 오도메트리 업데이트
                pos_L, pos_R, pos_B = self.webots.get_encoder_values()
                self.odometry.update(pos_L, pos_R, pos_B)
                
                # 5. 현재 위치 얻기
                x, y, theta = self.odometry.get_pose()
                
                # 6. TF 메시지 변환 (controller에서 계산!)
                t_odom = self.tf_converter.create_odometry_transform(
                    x, y, theta, self.ros_bridge
                )
                
                # 7. ROS 발행 (ros_bridge는 그냥 발행만!)
                self.ros_bridge.publish_transform(t_odom)
                
                # 8. 라이다 스캔 메시지 변환 및 발행
                lidar_data = self.webots.get_lidar_data()
                scan_msg = self.tf_converter.create_laser_scan_msg(
                    lidar_data['ranges'],
                    lidar_data['fov'],
                    lidar_data['min_range'],
                    lidar_data['max_range'],
                    self.ros_bridge
                )
                self.ros_bridge.publish_scan(scan_msg)
                
                # 로그 출력 (100 스텝마다)
                step_count += 1
                if step_count % log_interval == 0:
                    print(f"[Step {step_count}] Pos: ({x:.3f}, {y:.3f}), Theta: {theta:.3f}")
        
        except KeyboardInterrupt:
            print("\n⏹️ Interrupt received, shutting down...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """정리 작업"""
        print("🧹 Cleaning up...")
        self.webots.stop()
        shutdown_ros_node()
        print("✅ Shutdown complete")


def main():
    """프로그램 진입점"""
    controller = HanulController()
    controller.run()


if __name__ == '__main__':
    main()
