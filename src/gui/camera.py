"""
camera.py
Simple free-fly camera: WASD to move, mouse drag to look around, scroll to zoom.
"""

import math
import numpy as np
from pyrr import matrix44, vector3


class Camera:
    def __init__(self, position=(0.0, 15.0, 40.0)):
        self.position = np.array(position, dtype=np.float32)
        self.yaw = -90.0
        self.pitch = -20.0
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.speed = 20.0
        self.sensitivity = 0.1
        self._update_vectors()

    def _update_vectors(self):
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        front = np.array([
            math.cos(rad_yaw) * math.cos(rad_pitch),
            math.sin(rad_pitch),
            math.sin(rad_yaw) * math.cos(rad_pitch)
        ], dtype=np.float32)
        self.front = front / np.linalg.norm(front)

    def process_keyboard(self, direction, dt):
        velocity = self.speed * dt
        right = np.cross(self.front, self.up)
        right = right / np.linalg.norm(right)

        if direction == "FORWARD":
            self.position += self.front * velocity
        elif direction == "BACKWARD":
            self.position -= self.front * velocity
        elif direction == "LEFT":
            self.position -= right * velocity
        elif direction == "RIGHT":
            self.position += right * velocity

    def process_mouse(self, dx, dy):
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self._update_vectors()

    def get_view_matrix(self, shake_offset=None):
        eye = self.position if shake_offset is None else self.position + shake_offset
        target = eye + self.front
        return matrix44.create_look_at(eye, target, self.up).astype(np.float32)

    def focus_on(self, world_pos, body_radius):
        """
        Snap the camera to a good viewing distance/angle for a body, then
        hand control back to free-fly (WASD/mouse still work afterward).
        """
        world_pos = np.array(world_pos, dtype=np.float32)
        distance = max(body_radius * 6.0, 3.0)
        offset = np.array([distance * 0.6, distance * 0.35, distance], dtype=np.float32)
        self.position = world_pos + offset

        direction = world_pos - self.position
        direction = direction / np.linalg.norm(direction)
        self.pitch = math.degrees(math.asin(direction[1]))
        self.yaw = math.degrees(math.atan2(direction[2], direction[0]))
        self._update_vectors()

    def start_ease_to(self, world_pos, body_radius):
        """Begin a smooth (lerped) transition to frame a body -- used by click-to-inspect."""
        world_pos = np.array(world_pos, dtype=np.float32)
        distance = max(body_radius * 6.0, 3.0)
        offset = np.array([distance * 0.6, distance * 0.35, distance], dtype=np.float32)
        target_pos = world_pos + offset

        direction = world_pos - target_pos
        direction = direction / np.linalg.norm(direction)
        target_pitch = math.degrees(math.asin(direction[1]))
        target_yaw = math.degrees(math.atan2(direction[2], direction[0]))

        self._ease_target_pos = target_pos
        self._ease_target_yaw = target_yaw
        self._ease_target_pitch = target_pitch
        self.easing = True

    def update_easing(self, dt):
        """Call once per frame; smoothly interpolates toward the ease target, then stops."""
        if not getattr(self, "easing", False):
            return
        t = min(1.0, dt * 4.0)  # exponential-ish ease speed
        self.position += (self._ease_target_pos - self.position) * t

        yaw_diff = (self._ease_target_yaw - self.yaw + 540) % 360 - 180
        self.yaw += yaw_diff * t
        self.pitch += (self._ease_target_pitch - self.pitch) * t
        self._update_vectors()

        if (np.linalg.norm(self._ease_target_pos - self.position) < 0.05
                and abs(yaw_diff) < 0.5):
            self.easing = False

    def trigger_shake(self, intensity=0.6, duration=0.5):
        """Kicks off a short camera-shake, e.g. when a planet is destroyed."""
        self._shake_intensity = intensity
        self._shake_duration = duration
        self._shake_timer = duration

    def get_shake_offset(self, dt):
        """Call once per frame to decay the shake timer and get a small random offset."""
        timer = getattr(self, "_shake_timer", 0.0)
        if timer <= 0.0:
            return np.zeros(3, dtype=np.float32)
        self._shake_timer = max(0.0, timer - dt)
        falloff = self._shake_timer / max(self._shake_duration, 1e-4)
        strength = self._shake_intensity * falloff
        return (np.random.uniform(-1, 1, 3) * strength).astype(np.float32)
