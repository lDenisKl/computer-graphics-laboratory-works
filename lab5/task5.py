import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lab3"))
from task3 import bresenham_line

with open(Path(__file__).parent / "data.json", encoding="utf-8") as f:
    d = json.load(f)

polygon = [tuple(p) for p in d["polygon"]]

W = max(p[0] for p in polygon) + 8
H = max(p[1] for p in polygon) + 8


def rasterize_outline(verts, W, H):
    """
    Растеризация рёбер для XOR-заливки: ровно один пиксель на строку y.
    Стандартный Bresenham не подходит — для пологих рёбер (|dx|>|dy|) он
    кладёт несколько пикселей в одну строку, нарушая чётность пересечений.
    Используем линейную интерполяцию по y: x = round(x0 + dx*(y-y0)/dy).
    Верхний конец включается через XOR (снимает дубли в вершинах-пиках),
    нижний конец исключается. Горизонтальные рёбра пропускаются.
    """
    grid = np.zeros((H, W), dtype=np.int8)
    n = len(verts)
    for i in range(n):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % n]
        if y0 == y1:
            continue
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx = x1 - x0
        dy = y1 - y0
        for step in range(dy):          # y0..y1-1: верх включён, низ исключён
            y = y0 + step
            x = round(x0 + dx * step / dy)
            if 0 <= x < W and 0 <= y < H:
                grid[y, x] ^= 1
    return grid


def xor_fill_snapshots(outline, n_snapshots=9):
    """
    Применяет XOR-заливку строка за строкой:
      I(x+1, y) = I(x, y) XOR I(x+1, y),  x = 0, 1, ..., W-2
    Возвращает список снимков состояния растра для пошаговой демонстрации.
    """
    H, W = outline.shape
    grid = outline.copy()
    snaps = [(grid.copy(), "Шаг 0: растеризованный контур многоугольника")]

    step = max(1, H // (n_snapshots - 1))
    for y in range(H):
        for x in range(W - 1):
            grid[y, x + 1] ^= grid[y, x]
        if (y + 1) % step == 0 or y == H - 1:
            label = (
                "Результат: заливка завершена"
                if y == H - 1
                else f"Обработаны строки 0 – {y}"
            )
            snaps.append((grid.copy(), label))

    return snaps


outline = rasterize_outline(polygon, W, H)
snaps = xor_fill_snapshots(outline, n_snapshots=9)

# Пиксели контура по Брезенхему — для визуальной накладки на каждом кадре
contour_pixels = []
n = len(polygon)
for i in range(n):
    contour_pixels.extend(bresenham_line(*polygon[i], *polygon[(i + 1) % n]))
contour_xs = [p[0] for p in contour_pixels]
contour_ys = [p[1] for p in contour_pixels]

cols = 4
n_rows = (len(snaps) + cols - 1) // cols
cmap = mcolors.ListedColormap(["white", "#1565C0"])

fig, axes = plt.subplots(n_rows, cols, figsize=(cols * 4.2, n_rows * 4.2))
axes_flat = np.array(axes).flatten()

for idx, (g, label) in enumerate(snaps):
    ax = axes_flat[idx]
    ax.imshow(g, cmap=cmap, vmin=0, vmax=1,
              interpolation="nearest", origin="upper", aspect="equal")
    ax.scatter(contour_xs, contour_ys, color="red", s=1.5, alpha=0.6, linewidths=0)
    ax.set_title(label, fontsize=8, pad=4)
    ax.tick_params(labelsize=6)
    ax.set_xlabel("x", fontsize=7)
    ax.set_ylabel("y", fontsize=7)

for idx in range(len(snaps), len(axes_flat)):
    axes_flat[idx].set_visible(False)

fig.suptitle(
    "Лабораторная работа 5 — Вариант 3\n"
    "Алгоритм XOR: пошаговая заливка многоугольника",
    fontsize=12, fontweight="bold",
)
plt.tight_layout()
plt.show()
