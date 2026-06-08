"""Birinci şahıs (FPS) kamera.

- WASD: ileri / sol / geri / sağ (yatay düzlemde, yere paralel)
- Mouse: bakış yönü (yaw + pitch)
- Hareket hızı delta-time ile ölçeklenir, FPS'ten bağımsız hız sağlar
"""

from __future__ import annotations

import math

import glfw
import glm


class Camera:
    def __init__(self, position: glm.vec3, yaw: float = -90.0, pitch: float = 0.0) -> None:
        # Açılar derece cinsinden tutulur, hesaplamalarda radyana çevrilir.
        self.position = glm.vec3(position)
        self.yaw = yaw
        self.pitch = pitch
        self.world_up = glm.vec3(0.0, 1.0, 0.0)

        self.move_speed = 4.0       # birim / saniye
        self.mouse_sensitivity = 0.1

        # Mouse delta hesabı için son fare pozisyonu.
        self._last_mouse_x: float | None = None
        self._last_mouse_y: float | None = None

        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self._recalculate_vectors()

    def _recalculate_vectors(self) -> None:
        yaw_r = math.radians(self.yaw)
        pitch_r = math.radians(self.pitch)
        front = glm.vec3(
            math.cos(yaw_r) * math.cos(pitch_r),
            math.sin(pitch_r),
            math.sin(yaw_r) * math.cos(pitch_r),
        )
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def get_view(self) -> glm.mat4:
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def process_keyboard(self, window, dt: float) -> None:
        velocity = self.move_speed * dt
        # Y bileşenini sıfırlayarak hareketi yere paralel tutuyoruz —
        # yukarı bakınca öne basmak uçmaya yol açmasın.
        forward = glm.normalize(glm.vec3(self.front.x, 0.0, self.front.z))
        right = glm.normalize(glm.vec3(self.right.x, 0.0, self.right.z))

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position += forward * velocity
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position -= forward * velocity
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position -= right * velocity
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position += right * velocity

    def process_mouse(self, x: float, y: float) -> None:
        if self._last_mouse_x is None:
            self._last_mouse_x = x
            self._last_mouse_y = y
            return

        dx = x - self._last_mouse_x
        dy = self._last_mouse_y - y  # ekran y aşağı pozitif, biz yukarıyı pozitif sayıyoruz
        self._last_mouse_x = x
        self._last_mouse_y = y

        self.yaw += dx * self.mouse_sensitivity
        self.pitch += dy * self.mouse_sensitivity

        # Tepetaklak olmayı engellemek için pitch'i sınırla
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        self._recalculate_vectors()
