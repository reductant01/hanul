#!/usr/bin/env bash
# 현재 다이나믹셀 바퀴 엔코더 값을 1회 읽어서 출력.
# 사용:
#   ./scripts/echo_wheel_encoder.sh
#   MOTOR_PORT=/dev/ttyUSB1 ./scripts/echo_wheel_encoder.sh
#   MOTOR_ID_LEFT=3 MOTOR_ID_RIGHT=1 MOTOR_ID_BACK=2 ./scripts/echo_wheel_encoder.sh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

if [ -f /opt/ros/jazzy/setup.bash ]; then
  # 현재 프로젝트 실행 환경과 맞추기 위해 ROS 환경이 있으면 함께 로드.
  # 이 스크립트 자체는 ROS 토픽을 쓰지 않는다.
  source /opt/ros/jazzy/setup.bash
fi

export MOTOR_PORT="${MOTOR_PORT:-/dev/wheel}"
export DXL_BAUDRATE="${DXL_BAUDRATE:-1000000}"
export MOTOR_ID_LEFT="${MOTOR_ID_LEFT:-3}"
export MOTOR_ID_RIGHT="${MOTOR_ID_RIGHT:-1}"
export MOTOR_ID_BACK="${MOTOR_ID_BACK:-2}"

python3 - <<'PY'
import math
import os
import sys

try:
    from dynamixel_sdk import PacketHandler, PortHandler
except ImportError:
    print("dynamixel_sdk를 찾지 못했습니다. 현재 NUC/가상환경에서 설치 상태를 확인해주세요.", file=sys.stderr)
    sys.exit(1)

from controllers.hanul_controller.hanul_hardware import (
    ADDR_PRESENT_POSITION,
    BAUDRATE,
    PROTOCOL_VERSION,
    TICK_TO_RAD,
    _to_signed_32bit,
)

port_name = os.environ.get("MOTOR_PORT", "/dev/wheel")
baudrate = int(os.environ.get("DXL_BAUDRATE", str(BAUDRATE)))
motor_ids = [
    ("left", int(os.environ.get("MOTOR_ID_LEFT", "3"))),
    ("right", int(os.environ.get("MOTOR_ID_RIGHT", "1"))),
    ("back", int(os.environ.get("MOTOR_ID_BACK", "2"))),
]

port_handler = PortHandler(port_name)
packet_handler = PacketHandler(PROTOCOL_VERSION)

if not os.path.exists(port_name):
    print(f"모터 포트를 찾지 못했습니다: {port_name}", file=sys.stderr)
    print("예: MOTOR_PORT=/dev/ttyUSB1 ./scripts/echo_wheel_encoder.sh", file=sys.stderr)
    sys.exit(1)

if not port_handler.openPort():
    print(f"포트를 열지 못했습니다: {port_name}", file=sys.stderr)
    print("권한 문제면 sudo chmod 666 /dev/wheel 또는 올바른 포트를 확인해주세요.", file=sys.stderr)
    sys.exit(1)

if not port_handler.setBaudRate(baudrate):
    print(f"보드레이트 설정에 실패했습니다: {baudrate}", file=sys.stderr)
    port_handler.closePort()
    sys.exit(1)

print("")
print("현재 바퀴 다이나믹셀 엔코더 값")
print(f"port={port_name} baudrate={baudrate}")
print("")

try:
    for name, motor_id in motor_ids:
        raw, comm_result, dxl_error = packet_handler.read4ByteTxRx(
            port_handler, motor_id, ADDR_PRESENT_POSITION
        )
        if comm_result != 0 or dxl_error != 0:
            comm_msg = packet_handler.getTxRxResult(comm_result) if comm_result != 0 else "COMM_SUCCESS"
            err_msg = packet_handler.getRxPacketError(dxl_error) if dxl_error != 0 else "-"
            print(
                f"{name:>5} (ID {motor_id}): read failed | comm={comm_result} ({comm_msg}) | "
                f"packet_error={dxl_error} ({err_msg})"
            )
            continue

        signed = _to_signed_32bit(raw)
        rad = signed * TICK_TO_RAD
        rev = rad / (2.0 * math.pi)
        print(
            f"{name:>5} (ID {motor_id}): raw={raw:<10} signed={signed:<10} "
            f"rad={rad:>12.6f} rev={rev:>10.6f}"
        )
finally:
    port_handler.closePort()

print("")
PY
