#!/usr/bin/env python3
"""
Nav2 핵심 lifecycle 노드들이 active가 될 때까지 대기.

사용법:
  python3 scripts/wait_nav2_active.py [timeout_sec]
  python3 scripts/wait_nav2_active.py 30 /planner_server /controller_server /bt_navigator /behavior_server

기본 대기 노드:
  /planner_server
  /controller_server
  /bt_navigator
  /behavior_server

종료 코드:
  0 = 모든 대상 노드 active
  1 = 타임아웃 또는 오류
"""
import subprocess
import sys
import time


DEFAULT_NODES = [
    "/planner_server",
    "/controller_server",
    "/bt_navigator",
    "/behavior_server",
]


def _normalize_node_name(name):
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


def main():
    timeout_sec = 30.0
    nodes = []

    for arg in sys.argv[1:]:
        if not nodes:
            try:
                timeout_sec = float(arg)
                continue
            except ValueError:
                pass
        nodes.append(_normalize_node_name(arg))

    if not nodes:
        nodes = list(DEFAULT_NODES)

    deadline = time.monotonic() + timeout_sec
    last_states = {}

    while time.monotonic() < deadline:
        all_active = True

        for node_name in nodes:
            state = _get_lifecycle_state(node_name)
            if last_states.get(node_name) != state:
                print(f"[nav2] {node_name} state: {state or 'unavailable'}")
                last_states[node_name] = state
            if state != "active":
                all_active = False

        if all_active:
            print("[nav2] all target lifecycle nodes are active")
            return 0

        time.sleep(1.0)

    print("[nav2] timeout waiting for lifecycle nodes to become active", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
