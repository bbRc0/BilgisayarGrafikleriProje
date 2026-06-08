"""Labirent oyunu - başlangıç iskeleti.

Şimdilik sadece GLFW penceresi açıyor ve OpenGL context'in çalıştığını
doğruluyor. Sonraki adımlarda kamera, shader, labirent geometrisi,
texture, ışıklandırma ve çarpışma kontrolü eklenecek.
"""

import sys

import glfw
from OpenGL import GL


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Labirent Oyunu - Bilgisayar Grafikleri Projesi"


def on_key(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)


def on_framebuffer_size(window, width, height):
    GL.glViewport(0, 0, width, height)


def main() -> int:
    if not glfw.init():
        print("GLFW baslatilamadi", file=sys.stderr)
        return 1

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        print("Pencere olusturulamadi", file=sys.stderr)
        return 1

    glfw.make_context_current(window)
    glfw.set_key_callback(window, on_key)
    glfw.set_framebuffer_size_callback(window, on_framebuffer_size)

    print("OpenGL satıcı : ", GL.glGetString(GL.GL_VENDOR).decode(), flush=True)
    print("OpenGL sürüm  : ", GL.glGetString(GL.GL_VERSION).decode(), flush=True)
    print("GLSL sürüm    : ", GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode(), flush=True)

    GL.glEnable(GL.GL_DEPTH_TEST)

    while not glfw.window_should_close(window):
        GL.glClearColor(0.10, 0.12, 0.16, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
