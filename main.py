"""Labirent oyunu - 3. adım: FPS kamera (WASD + mouse).

Sahnede 3x3 grid halinde sabit küpler var ki kamera hareket ederken
mekândaki konumun değiştiği görülebilsin. Sonraki adımlarda bu küpler
labirent duvarlarına dönüşecek.
"""

import sys
from pathlib import Path

import glfw
import glm
from OpenGL import GL

from src.camera import Camera
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

    # FPS oyunlarında olduğu gibi mouse'u yakala ve gizle.
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    print("OpenGL satıcı : ", GL.glGetString(GL.GL_VENDOR).decode(), flush=True)
    print("OpenGL sürüm  : ", GL.glGetString(GL.GL_VERSION).decode(), flush=True)
    print("GLSL sürüm    : ", GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode(), flush=True)

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glCullFace(GL.GL_BACK)

    shader = Shader(PROJECT_ROOT / "shaders" / "basic.vert", PROJECT_ROOT / "shaders" / "basic.frag")
    cube = Cube()

    camera = Camera(position=glm.vec3(0.0, 1.0, 6.0))
    glfw.set_cursor_pos_callback(window, lambda w, x, y: camera.process_mouse(x, y))

    projection = glm.perspective(glm.radians(60.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)

    # Test sahnesi: 3x3 grid küpler (z=0 düzleminde)
    cube_positions = [
        glm.vec3(x * 2.5, 0.5, z * 2.5)
        for x in (-1, 0, 1)
        for z in (-1, 0, 1)
    ]
    cube_colors = [
        glm.vec3(0.85, 0.55, 0.25),
        glm.vec3(0.45, 0.70, 0.35),
        glm.vec3(0.30, 0.55, 0.85),
        glm.vec3(0.85, 0.40, 0.60),
        glm.vec3(0.75, 0.75, 0.30),
        glm.vec3(0.55, 0.40, 0.80),
        glm.vec3(0.40, 0.80, 0.75),
        glm.vec3(0.90, 0.65, 0.45),
        glm.vec3(0.65, 0.65, 0.65),
    ]

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        now = glfw.get_time()
        dt = now - last_time
        last_time = now

        camera.process_keyboard(window, dt)

        GL.glClearColor(0.10, 0.12, 0.16, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        view = camera.get_view()

        shader.use()
        shader.set_mat4("uProjection", projection)
        shader.set_mat4("uView", view)

        for pos, color in zip(cube_positions, cube_colors):
            model = glm.translate(glm.mat4(1.0), pos)
            shader.set_mat4("uModel", model)
            shader.set_vec3("uColor", color)
            cube.draw()

        glfw.swap_buffers(window)
        glfw.poll_events()

    cube.delete()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
