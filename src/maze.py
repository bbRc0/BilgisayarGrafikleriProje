"""Statik labirent grid'i.

Labirent 2B bir tamsayı dizisi olarak tutulur:
    1 = duvar, 0 = yol
Grid'in (gx, gz) hücresi dünyada (gx * CELL_SIZE, *, gz * CELL_SIZE)
konumunda durur. Y ekseni yukarı doğrudur; zemin y=0'da, duvarlar
y=0..WALL_HEIGHT arasında yükselir.
"""

from __future__ import annotations

import glm


CELL_SIZE = 2.0
WALL_HEIGHT = 2.0


# 10x10 statik harita. Köşeler hep duvar; içerde dolambaçlı koridorlar.
# Başlangıç hücresi (gx=1, gz=1) - sol üst köşeye yakın bir yol hücresi.
MAZE_DATA: list[list[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


class Maze:
    def __init__(self, grid: list[list[int]] | None = None) -> None:
        self.grid = grid if grid is not None else MAZE_DATA
        self.height = len(self.grid)         # z yönündeki hücre sayısı
        self.width = len(self.grid[0])       # x yönündeki hücre sayısı
        self.cell_size = CELL_SIZE
        self.wall_height = WALL_HEIGHT

    def is_wall(self, gx: int, gz: int) -> bool:
        if gx < 0 or gz < 0 or gx >= self.width or gz >= self.height:
            return True
        return self.grid[gz][gx] == 1

    def wall_positions(self) -> list[glm.vec3]:
        """Duvar hücrelerinin dünya merkez konumlarını döndürür (cube center)."""
        positions: list[glm.vec3] = []
        for gz in range(self.height):
            for gx in range(self.width):
                if self.grid[gz][gx] == 1:
                    positions.append(
                        glm.vec3(
                            gx * self.cell_size,
                            self.wall_height * 0.5,
                            gz * self.cell_size,
                        )
                    )
        return positions

    def floor_center(self) -> glm.vec3:
        """Zemin merkezinin dünya konumu (y ekseninde 0'ın hemen altında)."""
        return glm.vec3(
            (self.width - 1) * self.cell_size * 0.5,
            -0.05,
            (self.height - 1) * self.cell_size * 0.5,
        )

    def floor_scale(self) -> glm.vec3:
        """Zemin için cube ölçeği (ince ve geniş bir levha)."""
        return glm.vec3(
            self.width * self.cell_size,
            0.1,
            self.height * self.cell_size,
        )

    def start_world_position(self, eye_height: float = 1.0) -> glm.vec3:
        """Oyuncunun başlangıç dünya konumu (yol olan ilk hücreye yerleştirir)."""
        for gz in range(self.height):
            for gx in range(self.width):
                if self.grid[gz][gx] == 0:
                    return glm.vec3(
                        gx * self.cell_size,
                        eye_height,
                        gz * self.cell_size,
                    )
        return glm.vec3(0.0, eye_height, 0.0)
