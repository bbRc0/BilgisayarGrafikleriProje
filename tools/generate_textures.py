"""assets/ altına basit prosedürel duvar ve zemin dokuları üretir.

Bir kez çalıştırılır:
    python tools/generate_textures.py

Üretilen PNG'ler git'e commit'lenir. Kullanıcı daha güzel dokular
istiyorsa wall.png ve floor.png'yi internetten / kendi seçimiyle
değiştirebilir; texture loader dosya formatına bakmıyor.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


SIZE = 256
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _luminance_noise(rng: np.random.Generator, shape: tuple[int, int], sigma: float) -> np.ndarray:
    """Tek kanal Gaussian gürültü — sonra RGB'ye broadcast edilir.

    Her kanal için ayrı gürültü üretmek 'TV karıncalanması' tarzı renkli
    benekler oluşturur. Tek kanallı gürültüyü 3 kanala kopyalamak ise
    sadece parlaklık varyasyonu yaratır, doğal görünür.
    """
    return rng.normal(0.0, sigma, shape).astype(np.float32)


def _smooth_noise(rng: np.random.Generator, target: int, low_res: int, amp: float) -> np.ndarray:
    """Düşük çözünürlüklü gürültüyü büyüterek yumuşak büyük lekeler üretir."""
    small = rng.normal(128.0, amp, (low_res, low_res)).astype(np.float32)
    small = np.clip(small, 0, 255).astype(np.uint8)
    big = Image.fromarray(small, mode="L").resize((target, target), Image.BILINEAR)
    return np.asarray(big, dtype=np.float32) - 128.0  # merkezi sıfıra çek


def make_wall(seed: int = 42) -> Image.Image:
    """Kayık dizilmiş taş tuğla dokusu (luminance bazlı varyasyon)."""
    rng = np.random.default_rng(seed)

    base_color = np.array([165, 85, 60], dtype=np.float32)    # kırmızı tuğla
    mortar_color = np.array([80, 70, 58], dtype=np.float32)   # koyu derz harcı

    img = np.tile(mortar_color, (SIZE, SIZE, 1))  # önce her şey derz, üstüne tuğlalar

    brick_w, brick_h = 64, 32
    mortar = 2  # derz kalınlığı

    for row in range(SIZE // brick_h):
        offset = (brick_w // 2) if row % 2 else 0
        y0 = row * brick_h
        for col in range(-1, SIZE // brick_w + 1):
            x0 = col * brick_w + offset
            x_start = max(0, x0) + mortar
            x_end = min(SIZE, x0 + brick_w)
            y_start = y0 + mortar
            y_end = min(SIZE, y0 + brick_h)
            if x_start >= x_end or y_start >= y_end:
                continue

            # Bu tuğlaya özgü tek parlaklık kayması (tüm kanalları eşit etkiler)
            shift = float(rng.uniform(-18.0, 18.0))
            img[y_start:y_end, x_start:x_end] = base_color + shift

    # Tüm yüzeye luminance grain (TV karıncalanması değil!)
    grain = _luminance_noise(rng, (SIZE, SIZE), sigma=6.0)
    img += grain[:, :, None]

    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")


def make_floor(seed: int = 123) -> Image.Image:
    """Koyu ahşap parke zemin: yatay uzun tahtalar + dikey lifler + ton varyasyonu."""
    rng = np.random.default_rng(seed)

    base_color = np.array([105, 70, 45], dtype=np.float32)     # koyu kahverengi ahşap
    gap_color = np.array([35, 22, 12], dtype=np.float32)       # tahtalar arası ince derz

    # Önce her şey gap, üstüne tahtaları çizeceğiz
    img = np.tile(gap_color, (SIZE, SIZE, 1))

    plank_h = 32   # her tahta 32 piksel yüksek
    gap = 1        # tahtalar arası 1 piksel boşluk

    xs = np.arange(SIZE, dtype=np.float32)
    for row in range(SIZE // plank_h):
        y_start = row * plank_h + gap
        y_end = (row + 1) * plank_h

        # Bu tahtaya özgü luminance kayması (her tahta biraz farklı renk olsun)
        shift = float(rng.uniform(-20.0, 20.0))
        img[y_start:y_end, :] = base_color + shift

        # Tahta lifleri: yatay dalgalı koyu çizgiler, sadece bu tahtanın aralığında
        n_grain = 4
        for _ in range(n_grain):
            y_line = float(rng.uniform(y_start + 1, y_end - 1))
            amp = float(rng.uniform(0.4, 1.6))
            freq = float(rng.uniform(0.03, 0.10))
            phase = float(rng.uniform(0.0, 2.0 * np.pi))
            darken = float(rng.uniform(0.78, 0.92))
            y_offsets = amp * np.sin(xs * freq + phase)
            y_idx = (y_line + y_offsets).astype(np.int32)
            valid = (y_idx >= y_start) & (y_idx < y_end)
            img[y_idx[valid], xs[valid].astype(np.int32)] *= darken

        # Düğüm (knot): tahta üzerinde rastgele yerde küçük koyu nokta
        if rng.random() < 0.5:
            kx = int(rng.integers(10, SIZE - 10))
            ky = int(rng.integers(y_start + 4, y_end - 4))
            kr = int(rng.integers(2, 4))
            for dy in range(-kr, kr + 1):
                for dx in range(-kr, kr + 1):
                    if dx * dx + dy * dy <= kr * kr:
                        yi, xi = ky + dy, kx + dx
                        if y_start <= yi < y_end and 0 <= xi < SIZE:
                            img[yi, xi] *= 0.55

    # İnce yüzey grain (tek kanal, luminance)
    grain = _luminance_noise(rng, (SIZE, SIZE), sigma=4.0)
    img += grain[:, :, None]

    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    wall_path = ASSETS_DIR / "wall.png"
    floor_path = ASSETS_DIR / "floor.png"

    make_wall().save(wall_path)
    make_floor().save(floor_path)

    print(f"Yazildi: {wall_path}")
    print(f"Yazildi: {floor_path}")


if __name__ == "__main__":
    main()
