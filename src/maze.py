"""Labirent grid'i ve oluşturucu.

Labirent 2B bir tamsayı dizisi olarak tutulur:
    1 = duvar, 0 = yol
Grid'in (gx, gz) hücresi dünyada (gx * CELL_SIZE, *, gz * CELL_SIZE)
konumunda durur. Y ekseni yukarı doğrudur; zemin y=0'da, duvarlar
y=0..WALL_HEIGHT arasında yükselir.

MAZE_DATA, deterministik bir DFS recursive backtracker ile sabit seed
kullanılarak üretilir. Her programa çalıştırmada AYNI labirent çıkar
(statik gibi davranır) ama elle yazılmak yerine algoritmik üretildiği
için büyük boyutlarda da düzgün dolambaçlı koridorlar üretebiliyoruz.
"""

from __future__ import annotations

import random

import glm


CELL_SIZE = 2.0
WALL_HEIGHT = 2.0

MAZE_WIDTH = 21        # toplam grid kenar uzunluğu (tek sayı olmalı)
MAZE_HEIGHT = 21
MAZE_SEED = 42         # üretici tohumu — değiştirilince labirent değişir
MAZE_LOOP_CHANCE = 0.22  # DFS sonrası "loop" oluşturmak için duvar kırma olasılığı


def build_maze(
    width: int,
    height: int,
    seed: int,
    loop_chance: float = 0.0,
) -> list[list[int]]:
    """Iterative DFS recursive backtracker ile labirent üretir.

    1. DFS ile bir "perfect maze" çıkar: her iki yol hücresi arasında
       tek bir yol vardır (yani tüm yollar dallanmış bir ağaç).
    2. loop_chance > 0 ise, iki yol hücresini ayıran iç duvarların bir
       kısmı rastgele kırılır — böylece labirentte alternatif yollar
       ve "loop"lar oluşur (perfect değil, "braided" maze).

    Width/height tek sayı olmalı; çift indeksler duvar grid'i, tek
    indeksler yol grid'i diye düşünülür.
    """
    if width % 2 == 0 or height % 2 == 0:
        raise ValueError("Maze boyutları tek sayı olmalı")

    grid: list[list[int]] = [[1] * width for _ in range(height)]
    rng = random.Random(seed)

    # 1) DFS recursive backtracker
    stack: list[tuple[int, int]] = [(1, 1)]
    grid[1][1] = 0

    while stack:
        x, y = stack[-1]
        neighbors = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        rng.shuffle(neighbors)
        carved = False
        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and grid[ny][nx] == 1:
                grid[y + dy // 2][x + dx // 2] = 0
                grid[ny][nx] = 0
                stack.append((nx, ny))
                carved = True
                break
        if not carved:
            stack.pop()

    # 2) Loop oluşturma (braiding): iki yol hücresini ayıran iç
    #    duvarların bir kısmını rastgele kır.
    if loop_chance > 0:
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if grid[y][x] != 1:
                    continue
                # Yatay komşular yol mu? → bu duvar dikey, iki yatay yolu ayırıyor
                if (
                    y % 2 == 1 and x % 2 == 0
                    and grid[y][x - 1] == 0 and grid[y][x + 1] == 0
                ):
                    if rng.random() < loop_chance:
                        grid[y][x] = 0
                # Dikey komşular yol mu? → bu duvar yatay, iki dikey yolu ayırıyor
                elif (
                    y % 2 == 0 and x % 2 == 1
                    and grid[y - 1][x] == 0 and grid[y + 1][x] == 0
                ):
                    if rng.random() < loop_chance:
                        grid[y][x] = 0

    return grid


MAZE_DATA: list[list[int]] = build_maze(
    MAZE_WIDTH, MAZE_HEIGHT, MAZE_SEED, loop_chance=MAZE_LOOP_CHANCE
)


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

    def exit_world_position(self, height: float = 1.0) -> glm.vec3:
        """Labirentin çıkışı: en uzak (sona en yakın) yol hücresi."""
        for gz in range(self.height - 1, -1, -1):
            for gx in range(self.width - 1, -1, -1):
                if self.grid[gz][gx] == 0:
                    return glm.vec3(
                        gx * self.cell_size,
                        height,
                        gz * self.cell_size,
                    )
        return glm.vec3(0.0, height, 0.0)
