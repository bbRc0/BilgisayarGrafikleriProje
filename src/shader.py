"""OpenGL shader programı için ince bir sarmalayıcı."""

from __future__ import annotations

from pathlib import Path

import glm
from OpenGL import GL


class Shader:
    def __init__(self, vertex_path: str | Path, fragment_path: str | Path) -> None:
        vertex_src = Path(vertex_path).read_text(encoding="utf-8")
        fragment_src = Path(fragment_path).read_text(encoding="utf-8")

        vs = self._compile(vertex_src, GL.GL_VERTEX_SHADER, vertex_path)
        fs = self._compile(fragment_src, GL.GL_FRAGMENT_SHADER, fragment_path)

        self.program = GL.glCreateProgram()
        GL.glAttachShader(self.program, vs)
        GL.glAttachShader(self.program, fs)
        GL.glLinkProgram(self.program)

        if not GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS):
            log = GL.glGetProgramInfoLog(self.program).decode(errors="replace")
            raise RuntimeError(f"Shader program link hatası:\n{log}")

        GL.glDeleteShader(vs)
        GL.glDeleteShader(fs)

        self._uniform_cache: dict[str, int] = {}

    @staticmethod
    def _compile(source: str, shader_type: int, where: str | Path) -> int:
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            log = GL.glGetShaderInfoLog(shader).decode(errors="replace")
            raise RuntimeError(f"Shader derleme hatası ({where}):\n{log}")
        return shader

    def use(self) -> None:
        GL.glUseProgram(self.program)

    def _loc(self, name: str) -> int:
        if name not in self._uniform_cache:
            self._uniform_cache[name] = GL.glGetUniformLocation(self.program, name)
        return self._uniform_cache[name]

    def set_mat4(self, name: str, value: glm.mat4) -> None:
        GL.glUniformMatrix4fv(self._loc(name), 1, GL.GL_FALSE, glm.value_ptr(value))

    def set_vec3(self, name: str, value: glm.vec3) -> None:
        GL.glUniform3f(self._loc(name), value.x, value.y, value.z)

    def set_float(self, name: str, value: float) -> None:
        GL.glUniform1f(self._loc(name), value)

    def set_int(self, name: str, value: int) -> None:
        GL.glUniform1i(self._loc(name), value)
