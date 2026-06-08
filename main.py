"""Labirent oyunu - 4. adım: statik labirent geometrisi.

10x10'luk sabit labirent. Duvarlar küp instance'ları olarak; zemin
ölçeklenmiş ince bir küp olarak çiziliyor. Kamera başlangıçta yol
hücresine yerleştiriliyor; çarpışma kontrolü henüz yok, duvarların
içinden geçebiliyorsun (sonraki adımda eklenecek).
"""

import sys
from pathlib import Path

import glfw
import glm
from OpenGL import GL

from src.camera import Camera
from src.maze import Maze
from src.mesh import Cube
from src.shader import Shader


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Labirent Oyunu - Bilgisayar Grafikleri Projesi"

PROJECT_ROOT = Path(__file__).resolve().parent

WALL_COLOR = glm.vec3(0.55, 0.50, 0.45)
FLOOR_COLOR = glm.vec3(0.20, 0.25, 0.20)


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
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    print("OpenGL satıcı : ", GL.glGetString(GL.GL_VENDOR).decode(), flush=True)
    print("OpenGL sürüm  : ", GL.glGetString(GL.GL_VERSION).decode(), flush=True)
    print("GLSL sürüm    : ", GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode(), flush=True)

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glCullFace(GL.GL_BACK)

    shader = Shader(PROJECT_ROOT / "shaders" / "basic.vert", PROJECT_ROOT / "shaders" / "basic.frag")
    cube = Cube()
    maze = Maze()

    camera = Camera(position=maze.start_world_position(eye_height=1.0))
    glfw.set_cursor_pos_callback(window, lambda w, x, y: camera.process_mouse(x, y))

    projection = glm.perspective(glm.radians(60.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)

    wall_positions = maze.wall_positions()
    wall_scale = glm.vec3(maze.cell_size, maze.wall_height, maze.cell_size)

    floor_model = glm.translate(glm.mat4(1.0), maze.floor_center())
    floor_model = glm.scale(floor_model, maze.floor_scale())

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

        # Zemin
        shader.set_mat4("uModel", floor_model)
        shader.set_vec3("uColor", FLOOR_COLOR)
        cube.draw()

        # Duvarlar
        shader.set_vec3("uColor", WALL_COLOR)
        for pos in wall_positions:
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.scale(model, wall_scale)
            shader.set_mat4("uModel", model)
            cube.draw()

        glfw.swap_buffers(window)
        glfw.poll_events()

    cube.delete()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
