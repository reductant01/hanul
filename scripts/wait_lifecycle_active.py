#!/usr/bin/env python3
"""
Lifecycle node가 active가 될 때까지 configure/activate를 재시도하며 대기.

사용법:
  python3 scripts/wait_lifecycle_active.py /map_server [timeout_sec] [sleep_sec]
  python3 scripts/wait_lifecycle_active.py amcl [timeout_sec] [sleep_sec]

종료 코드:
  0 = active 확인
  1 = 타임아웃 또는 오류
"""
import subprocess
import sys
import time


def _normalize_node_name(name):
    if not name:
        raise ValueError("node name is required")
    return name if name.startswith("/") else f"/{name}"


def _get_lifecycle_state(node_name):
    result = subprocess.run(
        ["ros2", "lifecycle", "get", node_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    line = (result.stdout or "").splitlines()
    if not line:
        return ""
    return line[0].strip().split()[0]


def _set_lifecycle_state(node_name, transition):
    subprocess.run(
        ["ros2", "lifecycle", "set", node_name, transition],
        check=False,
    )


def main():
    if len(sys.argv) < 2:
        print("사용법: python3 scripts/wait_lifecycle_active.py <node_name> [timeout_sec] [sleep_sec]", file=sys.stderr)
        return 1

    try:
        node_name = _normalize_node_name(sys.argv[1])
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        timeout_sec = float(sys.argv[2]) if len(sys.argv) >= 3 else 20.0
        sleep_sec = float(sys.argv[3]) if len(sys.argv) >= 4 else 1.0
    except ValueError:
        print("timeout_sec, sleep_sec 는 숫자여야 합니다.", file=sys.stderr)
        return 1

    deadline = time.monotonic() + timeout_sec
    last_state = None

    while time.monotonic() < deadline:
        state = _get_lifecycle_state(node_name)

        if state == "active":
            print(f"[lifecycle] {node_name} is active")
            return 0

        if state != last_state:
            print(f"[lifecycle] {node_name} state: {state or 'unavailable'}")
            last_state = state

        if state == "unconfigured":
            print(f"[lifecycle] configuring {node_name}")
            _set_lifecycle_state(node_name, "configure")
        elif state == "inactive":
            print(f"[lifecycle] activating {node_name}")
            _set_lifecycle_state(node_name, "activate")

        time.sleep(sleep_sec)

    print(f"[lifecycle] timeout waiting for {node_name} to become active", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
