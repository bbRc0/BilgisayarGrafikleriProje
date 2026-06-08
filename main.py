"""Labirent oyunu - 7. adım: AABB çarpışma kontrolü.

Oyuncu artık duvarlardan geçemez. Camera.process_keyboard her eksende
ayrı ayrı çarpışma kontrolü yapıyor: bir duvara çarpsan bile diğer
eksende kaymaya devam edebilirsin (wall sliding). Tüm zorunlu özellikler
tamamlandı.
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
from src.texture import Texture


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

    wall_tex = Texture(PROJECT_ROOT / "assets" / "wall.png")
    floor_tex = Texture(PROJECT_ROOT / "assets" / "floor.png")
    finish_tex = Texture(PROJECT_ROOT / "assets" / "finish.png")

    shader.use()
    shader.set_int("uTexture", 0)  # sampler texture unit 0'dan okusun

    # Aydınlatma uniform'ları (sahne boyunca sabit)
    light_dir = glm.normalize(glm.vec3(0.4, -1.0, 0.5))   # yukarıdan-yandan aşağı
    shader.set_vec3("uLightDir", light_dir)
    shader.set_vec3("uLightColor", glm.vec3(0.85, 0.82, 0.73))  # hafif sıcak, daha yumuşak güneş
    shader.set_vec3("uAmbient", glm.vec3(0.36, 0.36, 0.40))     # karanlık tarafı kaldıran ambient
    shader.set_float("uShininess", 32.0)
    shader.set_float("uSpecularStrength", 0.35)

    camera = Camera(position=maze.start_world_position(eye_height=1.0))
    glfw.set_cursor_pos_callback(window, lambda w, x, y: camera.process_mouse(x, y))

    projection = glm.perspective(glm.radians(60.0), WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)

    wall_positions = maze.wall_positions()
    wall_scale = glm.vec3(maze.cell_size, maze.wall_height, maze.cell_size)

    floor_model = glm.translate(glm.mat4(1.0), maze.floor_center())
    floor_model = glm.scale(floor_model, maze.floor_scale())

    finish_position = maze.exit_world_position(height=1.0)
    finish_scale = glm.vec3(0.7)

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        now = glfw.get_time()
        dt = now - last_time
        last_time = now

        camera.process_keyboard(window, dt, maze)

        GL.glClearColor(0.10, 0.12, 0.16, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        view = camera.get_view()

        shader.use()
        shader.set_mat4("uProjection", projection)
        shader.set_mat4("uView", view)
        shader.set_vec3("uViewPos", camera.position)

        # Zemin: dokuyu defalarca tile et, böylece plakalar net görünür
        floor_tex.bind(0)
        shader.set_float("uTexScale", 2.5)
        shader.set_mat4("uModel", floor_model)
        cube.draw()

        # Duvarlar: her duvar küpü 1 doku gösterir
        wall_tex.bind(0)
        shader.set_float("uTexScale", 1.0)
        for pos in wall_positions:
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.scale(model, wall_scale)
            shader.set_mat4("uModel", model)
            cube.draw()

        # FINISH küpü - labirentin sonunda Y ekseninde sürekli dönüyor.
        # Rotation şartını karşılar ve oyuna görsel hedef ekler.
        finish_tex.bind(0)
        finish_model = glm.translate(glm.mat4(1.0), finish_position)
        finish_model = glm.rotate(finish_model, now * 1.2, glm.vec3(0.0, 1.0, 0.0))
        finish_model = glm.scale(finish_model, finish_scale)
        shader.set_mat4("uModel", finish_model)
        cube.draw()

        glfw.swap_buffers(window)
        glfw.poll_events()

    cube.delete()
    wall_tex.delete()
    floor_tex.delete()
    finish_tex.delete()
    glfw.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
