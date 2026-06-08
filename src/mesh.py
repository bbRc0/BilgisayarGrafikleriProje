"""Temel mesh nesneleri (şimdilik birim küp)."""

from __future__ import annotations

import ctypes

import numpy as np
from OpenGL import GL


# Her satır: posX posY posZ normalX normalY normalZ texU texV
# Birim küp, merkez orijinde, kenar uzunluğu 1.0.
# Her yüz için 4 vertex, sıralama: BL -> BR -> TR -> TL (dış normal yönünden
# bakıldığında saatin tersi - CCW). Böylece OpenGL'in front-face=CCW
# kuralıyla back-face culling sorunsuz çalışır.
_CUBE_VERTICES = np.array(
    [
        # +Z yüzü (ön)
        -0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   0.0, 0.0,
         0.5, -0.5,  0.5,   0.0,  0.0,  1.0,   1.0, 0.0,
         0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   1.0, 1.0,
        -0.5,  0.5,  0.5,   0.0,  0.0,  1.0,   0.0, 1.0,
        # -Z yüzü (arka)
         0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   0.0, 0.0,
        -0.5, -0.5, -0.5,   0.0,  0.0, -1.0,   1.0, 0.0,
        -0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   1.0, 1.0,
         0.5,  0.5, -0.5,   0.0,  0.0, -1.0,   0.0, 1.0,
        # +X yüzü (sağ)
         0.5, -0.5,  0.5,   1.0,  0.0,  0.0,   0.0, 0.0,
         0.5, -0.5, -0.5,   1.0,  0.0,  0.0,   1.0, 0.0,
         0.5,  0.5, -0.5,   1.0,  0.0,  0.0,   1.0, 1.0,
         0.5,  0.5,  0.5,   1.0,  0.0,  0.0,   0.0, 1.0,
        # -X yüzü (sol)
        -0.5, -0.5, -0.5,  -1.0,  0.0,  0.0,   0.0, 0.0,
        -0.5, -0.5,  0.5,  -1.0,  0.0,  0.0,   1.0, 0.0,
        -0.5,  0.5,  0.5,  -1.0,  0.0,  0.0,   1.0, 1.0,
        -0.5,  0.5, -0.5,  -1.0,  0.0,  0.0,   0.0, 1.0,
        # +Y yüzü (üst)
        -0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   0.0, 0.0,
         0.5,  0.5,  0.5,   0.0,  1.0,  0.0,   1.0, 0.0,
         0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   1.0, 1.0,
        -0.5,  0.5, -0.5,   0.0,  1.0,  0.0,   0.0, 1.0,
        # -Y yüzü (alt)
        -0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   0.0, 0.0,
         0.5, -0.5, -0.5,   0.0, -1.0,  0.0,   1.0, 0.0,
         0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   1.0, 1.0,
        -0.5, -0.5,  0.5,   0.0, -1.0,  0.0,   0.0, 1.0,
    ],
    dtype=np.float32,
)

# Her yüz için 2 üçgen: (0,1,2) ve (2,3,0). Yüz başına 4 vertex olduğu için
# her bir yüzde indeksleri 4 kaydırıyoruz.
_CUBE_INDICES = np.array(
    [
         0,  1,  2,   2,  3,  0,
         4,  5,  6,   6,  7,  4,
         8,  9, 10,  10, 11,  8,
        12, 13, 14,  14, 15, 12,
        16, 17, 18,  18, 19, 16,
        20, 21, 22,  22, 23, 20,
    ],
    dtype=np.uint32,
)

_STRIDE = 8 * 4  # 8 float * 4 byte


class Cube:
    def __init__(self) -> None:
        self.vao = GL.glGenVertexArrays(1)
        self.vbo = GL.glGenBuffers(1)
        self.ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, _CUBE_VERTICES.nbytes, _CUBE_VERTICES, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, _CUBE_INDICES.nbytes, _CUBE_INDICES, GL.GL_STATIC_DRAW)

        # aPos
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, _STRIDE, ctypes.c_void_p(0))
        # aNormal
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, _STRIDE, ctypes.c_void_p(3 * 4))
        # aTexCoord
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribPointer(2, 2, GL.GL_FLOAT, GL.GL_FALSE, _STRIDE, ctypes.c_void_p(6 * 4))

        GL.glBindVertexArray(0)

        self.index_count = len(_CUBE_INDICES)

    def draw(self) -> None:
        GL.glBindVertexArray(self.vao)
        GL.glDrawElements(GL.GL_TRIANGLES, self.index_count, GL.GL_UNSIGNED_INT, None)

    def delete(self) -> None:
        GL.glDeleteVertexArrays(1, [self.vao])
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteBuffers(1, [self.ebo])
