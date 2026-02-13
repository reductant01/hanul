from controller import Robot, Keyboard

# 1. 로봇 초기화
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# 2. 키보드 활성화
keyboard = Keyboard()
keyboard.enable(timestep)

# 3. 모터 가져오기 (이름이 PROTO파일과 같아야 함)
motor_left = robot.getDevice("joint_wheel_left")
motor_right = robot.getDevice("joint_wheel_right")
motor_back = robot.getDevice("joint_wheel_back")

# 4. 모터 설정 (속도 제어 모드)
# 위치를 무한대(inf)로 설정해야 계속 회전합니다.
motors = [motor_left, motor_right, motor_back]
for motor in motors:
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)

# 5. 로봇 스펙 (속도 조절용)
MAX_SPEED = 10.0

print("Start Hanul Driver! Use W/A/S/D to move, Q/E to rotate.")

# --- 메인 루프 ---
while robot.step(timestep) != -1:
    # 6. 키보드 입력 받기
    key = keyboard.getKey()
    
    vx = 0  # 앞뒤 속도
    vy = 0  # 좌우 속도
    w  = 0  # 회전 속도

    if key == ord('W'): vx = 1      # 앞
    elif key == ord('S'): vx = -1   # 뒤
    elif key == ord('A'): vy = -1   # 왼쪽 (게걸음)
    elif key == ord('D'): vy = 1    # 오른쪽 (게걸음)
    elif key == ord('Q'): w = 1     # 왼쪽 회전
    elif key == ord('E'): w = -1    # 오른쪽 회전

    # 7. 3륜 옴니휠 운동학 (Kinematics) 계산
    # (벡터 분해 공식 적용)
    # v1: 왼쪽, v2: 오른쪽, v3: 뒤쪽
    
    # [공식]
    # 왼쪽 바퀴  = -0.5 * Vy + 0.866 * Vx + Rotation
    # 오른쪽 바퀴 = -0.5 * Vy - 0.866 * Vx + Rotation
    # 뒤쪽 바퀴  =  1.0 * Vy + Rotation
    
    # *주의: 모터 설치 방향에 따라 부호(+/-)가 반대일 수 있습니다.
    # 만약 키보드 반대로 움직이면 여기서 부호를 바꾸세요.
    
    vel_left  = (-0.5 * vy - 0.866 * vx + w) * MAX_SPEED
    vel_right = (-0.5 * vy + 0.866 * vx + w) * MAX_SPEED
    vel_back  = ( 1.0 * vy + w)              * MAX_SPEED

    # 8. 모터에 속도 명령 보내기
    motor_left.setVelocity(vel_left)
    motor_right.setVelocity(vel_right)
    motor_back.setVelocity(vel_back)