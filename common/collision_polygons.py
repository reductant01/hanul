"""
nav2_params.yaml에서 polygon 로드 및 PolygonStamped 메시지 생성. 발행은 ros_bridge.
"""
import ast
import math
import os

import yaml
from geometry_msgs.msg import PolygonStamped, Point32


def _load_stop_slow_from_nav2():
    project_root = os.environ.get('PROJECT_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_root, 'config', 'hanul', 'nav2_params.yaml')
    if not os.path.isfile(path):
        raise FileNotFoundError(f'config not found: {path}')
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    params = (data or {}).get('collision_monitor', {}).get('ros__parameters') or {}
    stop_raw = params.get('PolygonStop', {}).get('points')
    slow_raw = params.get('PolygonSlow', {}).get('points')
    if not isinstance(stop_raw, str) or not isinstance(slow_raw, str):
        raise ValueError('collision_monitor PolygonStop.points / PolygonSlow.points not found in nav2_params.yaml')
    stop = [tuple(p) for p in ast.literal_eval(stop_raw)]
    slow = [tuple(p) for p in ast.literal_eval(slow_raw)]
    if len(stop) < 3 or len(slow) < 3:
        raise ValueError('PolygonStop and PolygonSlow must have at least 3 points each in nav2_params.yaml')
    return stop, slow


_stop_points = None
_slowdown_points = None


def _get_stop_slow_points():
    global _stop_points, _slowdown_points
    if _stop_points is None:
        _stop_points, _slowdown_points = _load_stop_slow_from_nav2()
    return _stop_points, _slowdown_points


def _approach_points(n=24, r=0.17):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def create_polygon_stamped(frame_id, stamp, points_xy):
    msg = PolygonStamped()
    msg.header.frame_id = frame_id
    msg.header.stamp = stamp
    for x, y in points_xy:
        p = Point32()
        p.x = float(x)
        p.y = float(y)
        p.z = 0.0
        msg.polygon.points.append(p)
    return msg


def create_approach_polygon_stamped(frame_id, stamp, n=24, r=0.17):
    return create_polygon_stamped(frame_id, stamp, _approach_points(n=n, r=r))


def create_stop_polygon_stamped(frame_id, stamp):
    stop, _ = _get_stop_slow_points()
    return create_polygon_stamped(frame_id, stamp, stop)


def create_slowdown_polygon_stamped(frame_id, stamp):
    _, slow = _get_stop_slow_points()
    return create_polygon_stamped(frame_id, stamp, slow)
