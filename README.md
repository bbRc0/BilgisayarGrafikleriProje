# Labirent Oyunu

Bilgisayar Grafikleri dersi final projesi. OpenGL tabanlı, 3B, etkileşimli
labirent oyunu. Oyuncu birinci-şahıs bakışıyla labirentte gezer; duvarlardan
geçemez, koridorlardan ilerleyerek çıkışa ulaşmaya çalışır.

## Kullanılan Kütüphaneler

- [PyOpenGL](https://pypi.org/project/PyOpenGL/) - OpenGL bağlayıcısı
- [glfw](https://pypi.org/project/glfw/) - Pencere ve girdi yönetimi
- [PyGLM](https://pypi.org/project/PyGLM/) - Matris/vektör matematiği
- [NumPy](https://pypi.org/project/numpy/) - Vertex/index dizileri
- [Pillow](https://pypi.org/project/Pillow/) - Texture yükleme

## Kurulum

```powershell
# 1. Miniconda kurulu olmalı (https://docs.conda.io/en/latest/miniconda.html)

# 2. Ortamı oluştur
conda create -n grafik python=3.11 -y
conda activate grafik

# 3. Paketleri yükle
pip install -r requirements.txt
```

## Çalıştırma

```powershell
conda activate grafik
python main.py
```

## Kontrol Tuşları

| Tuş | İşlev |
|-----|-------|
| `W` `A` `S` `D` | Hareket (ileri / sol / geri / sağ) |
| Mouse | Kamera bakış yönü |
| `ESC` | Çıkış |

## Yazar

Ahmet Melih Üstüner
