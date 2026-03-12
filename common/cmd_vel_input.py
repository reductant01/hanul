#!/usr/bin/env python3
"""
키를 누르고 있을 때만 cmd_vel 발행, 손 떼면 정지.
teleop_twist_keyboard와 동일한 키 배치·속도 키(q/z w/x e/c) 사용.
발행: cmd_vel_unfiltered (collision_monitor 입력, 필터 전).
의존: pip install pynput
"""
import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from pynput import keyboard

if sys.platform != "win32":
    import termios



MOVE_BINDINGS = {
    'i': (1, 0, 0, 0),
    'o': (1, 0, 0, -1),
    'j': (0, 0, 0, 1),
    'l': (0, 0, 0, -1),
    'u': (1, 0, 0, 1),
    ',': (-1, 0, 0, 0),
    '.': (-1, 0, 0, 1),
    'm': (-1, 0, 0, -1),
    'O': (1, -1, 0, 0),
    'I': (1, 0, 0, 0),
    'J': (0, 1, 0, 0),
    'L': (0, -1, 0, 0),
    'U': (1, 1, 0, 0),
    '<': (-1, 0, 0, 0),
    '>': (-1, -1, 0, 0),
    'M': (-1, 1, 0, 0),
    't': (0, 0, 1, 0),
    'b': (0, 0, -1, 0),
}
SPEED_BINDINGS = {
    'q': (1.1, 1.1),
    'z': (0.9, 0.9),
    'w': (1.1, 1.0),
    'x': (0.9, 1.0),
    'e': (1.0, 1.1),
    'c': (1.0, 0.9),
}
VK_TO_CHAR = {44: ',', 46: '.'}


def _caps_lock_on():
    if sys.platform == "win32":
        try:
            import ctypes
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        except Exception:
            return False
    try:
        import subprocess
        out = subprocess.run(["xset", "q"], capture_output=True, text=True, timeout=1)
        return "Caps Lock:   on" in (out.stdout or "") or "Caps Lock: on" in (out.stdout or "")
    except Exception:
        return False


def key_to_binding_key(key, shift_pressed, caps_lock=False):
    if hasattr(key, 'char') and key.char:
        c = key.char
        if (shift_pressed or caps_lock) and c.isalpha():
            return c.upper()
        if shift_pressed and c == ',':
            return '<'
        if shift_pressed and c == '.':
            return '>'
        return c
    if hasattr(key, 'vk'):
        vk = key.vk
        if vk in (44, 60):
            return '<' if shift_pressed else ','
        if vk in (46, 62):
            return '>' if shift_pressed else '.'
        return VK_TO_CHAR.get(vk)
    return None


class CmdVelInputNode(Node):
    def __init__(self):
        super().__init__("cmd_vel_input")
        self._speed = 1.0
        self._turn = 1.0
        self._pressed = set()
        self._shift = False
        self._lock = __import__('threading').Lock()
        self._pub = self.create_publisher(Twist, "cmd_vel_unfiltered", 10)
        self._timer = self.create_timer(0.05, self._publish)

    def _apply_speed_key(self, binding_key):
        t = SPEED_BINDINGS.get(binding_key)
        if t:
            with self._lock:
                self._speed *= t[0]
                self._turn *= t[1]

    def _on_press(self, key):
        caps = _caps_lock_on()
        try:
            binding_key = key_to_binding_key(key, self._shift, caps)
        except Exception:
            binding_key = None
        if key == keyboard.Key.shift:
            self._shift = True
            return
        if binding_key in SPEED_BINDINGS:
            self._apply_speed_key(binding_key)
            return
        if binding_key in MOVE_BINDINGS:
            with self._lock:
                self._pressed.add(binding_key)

    def _on_release(self, key):
        if key == keyboard.Key.shift:
            self._shift = False
            return
        caps = _caps_lock_on()
        try:
            binding_key = key_to_binding_key(key, self._shift, caps)
        except Exception:
            binding_key = None
        if binding_key in MOVE_BINDINGS:
            with self._lock:
                self._pressed.discard(binding_key)
                if isinstance(binding_key, str) and len(binding_key) == 1 and binding_key.isalpha():
                    self._pressed.discard(binding_key.upper())
                    self._pressed.discard(binding_key.lower())

    def _publish(self):
        with self._lock:
            s, t = self._speed, self._turn
            pressed = set(self._pressed)
        twist = Twist()
        if not pressed:
            self._pub.publish(twist)
            return
        vx, vy, vz, th = 0.0, 0.0, 0.0, 0.0
        for k in pressed:
            b = MOVE_BINDINGS[k]
            vx += b[0]
            vy += b[1]
            vz += b[2]
            th += b[3]
        twist.linear.x = float(s * vx)
        twist.linear.y = float(s * vy)
        twist.linear.z = float(s * vz)
        twist.angular.z = float(t * th)
        self._pub.publish(twist)


def main():
    rclpy.init(args=sys.argv)
    node = CmdVelInputNode()
    node.get_logger().info(
        "Hold keys to move (release to stop). Unit scale (speed in omni_velocity).\n"
        "  Move: u i o / j k l / m , .  (Shift/Caps: strafe)\n"
        "  q/z w/x e/c: scale +-/10%%"
    )
    old_term = None
    if sys.platform != "win32" and sys.stdin.isatty():
        try:
            fd = sys.stdin.fileno()
            old_term = termios.tcgetattr(fd)
            new = termios.tcgetattr(fd)
            new[3] = new[3] & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSADRAIN, new)
        except Exception:
            old_term = None
    listener = keyboard.Listener(on_press=node._on_press, on_release=node._on_release)
    listener.start()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if old_term is not None:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term)
            except Exception:
                pass
        listener.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
