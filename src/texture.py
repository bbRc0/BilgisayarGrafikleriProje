"""Pillow ile yüklenmiş bir PNG'den OpenGL texture nesnesi oluşturur."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from OpenGL import GL
from PIL import Image


class Texture:
    def __init__(self, path: str | Path) -> None:
        image = Image.open(path).convert("RGBA")
        # OpenGL'in beklediği şekilde alt satır en başa gelsin.
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        data = np.frombuffer(image.tobytes(), dtype=np.uint8)
        width, height = image.size

        self.id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        # Anisotropic filtering: oblique (yatık) bakılan yüzeylerde texture'ın
        # bulanık/pikselli görünmesini önler. OpenGL 4.6 ile core; daha eski
        # sürümlerde EXT_texture_filter_anisotropic olarak vardır.
        GL_TEXTURE_MAX_ANISOTROPY = 0x84FE
        GL_MAX_TEXTURE_MAX_ANISOTROPY = 0x84FF
        try:
            buf = (GL.GLfloat * 1)()
            GL.glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY, buf)
            max_aniso = float(buf[0])
            if max_aniso > 1.0:
                GL.glTexParameterf(GL.GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY, min(max_aniso, 16.0))
        except Exception:
            pass

        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            width,
            height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            data,
        )
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def bind(self, unit: int = 0) -> None:
        GL.glActiveTexture(GL.GL_TEXTURE0 + unit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)

    def delete(self) -> None:
        GL.glDeleteTextures(1, [self.id])
