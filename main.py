"""Labirent oyunu - 2. adım: shader sistemi + ilk küp.

Şimdilik sabit bir kameradan, kendi etrafında dönen renkli bir küpe
bakıyoruz. Sonraki adımlarda kamera, labirent geometrisi, texture,
ışıklandırma ve çarpışma kontrolü eklenecek.
"""

import sys
from pathlib import Path

import glfw
import glm
from OpenGL import GL

from src.mesh import Cube
from src.shader import Shader


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Labirent Oyunu - Bilgisayar Grafikleri Projesi"

PROJECT_ROOT = Path(__file__).resolve().parent


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
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glCullFace(GL.GL_BACK)

    shader = Shader(PROJECT_ROOT / "shaders" / "basic.vert", PROJECT_ROOT / "shaders" / "basic.frag")
    cube = Cube()

    projection = glm.perspective(glm.radians(60.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)
    view = glm.lookAt(glm.vec3(2.5, 2.0, 3.5), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))

    while not glfw.window_should_close(window):
        t = glfw.get_time()

        GL.glClearColor(0.10, 0.12, 0.16, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        model = glm.mat4(1.0)
        model = glm.rotate(model, t * 0.7, glm.vec3(0.0, 1.0, 0.0))
        model = glm.rotate(model, t * 0.4, glm.vec3(1.0, 0.0, 0.0))

        shader.use()
        shader.set_mat4("uProjection", projection)
        shader.set_mat4("uView", view)
        shader.set_mat4("uModel", model)
        shader.set_vec3("uColor", glm.vec3(0.85, 0.55, 0.25))
        cube.draw()

        glfw.swap_buffers(window)
        glfw.poll_events()

    cube.delete()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
