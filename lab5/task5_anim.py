import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.animation as animation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lab3"))
from task3 import bresenham_line

with open(Path(__file__).parent / "data.json", encoding="utf-8") as f:
    d = json.load(f)

polygon = [tuple(p) for p in d["polygon"]]

W = max(p[0] for p in polygon) + 8
H = max(p[1] for p in polygon) + 8


def rasterize_outline(verts, W, H):
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
        for step in range(dy):
            y = y0 + step
            x = round(x0 + dx * step / dy)
            if 0 <= x < W and 0 <= y < H:
                grid[y, x] ^= 1
    return grid


def xor_fill_frames(outline, rows_per_frame=2):
    H, W = outline.shape
    grid = outline.copy()
    frames = []
    for y in range(H):
        for x in range(W - 1):
            grid[y, x + 1] ^= grid[y, x]
        if (y + 1) % rows_per_frame == 0 or y == H - 1:
            frames.append((grid.copy(), y))
    return frames


outline = rasterize_outline(polygon, W, H)
fill_frames = xor_fill_frames(outline, rows_per_frame=2)

final_fixed = fill_frames[-1][0].copy()
np.maximum(final_fixed, outline, out=final_fixed)

empty = np.zeros((H, W), dtype=np.int8)
anim_frames = (
    [(empty, "pre", -1)] * 6
    + [(outline, "outline", -1)] * 4
    + [(g, "fill", r) for g, r in fill_frames]
    + [(final_fixed, "done", -1)] * 6
)

contour_px = []
for i in range(len(polygon)):
    contour_px.extend(bresenham_line(*polygon[i], *polygon[(i + 1) % len(polygon)]))
cx = [p[0] for p in contour_px]
cy = [p[1] for p in contour_px]

poly_xs = [v[0] for v in polygon] + [polygon[0][0]]
poly_ys = [v[1] for v in polygon] + [polygon[0][1]]

cmap = mcolors.ListedColormap(["white", "#1565C0"])

fig, ax = plt.subplots(figsize=(7, 7))
ax.set_aspect("equal")

im = ax.imshow(
    anim_frames[0][0],
    cmap=cmap,
    vmin=0,
    vmax=1,
    interpolation="nearest",
    origin="upper",
    zorder=1,
)

border_scatter = ax.scatter(cx, cy, color="#E53935", s=4, zorder=4, alpha=0.0)

hline = ax.axhline(y=-2, color="orange", lw=1.5, ls="--", zorder=3, alpha=0.0)

(poly_line,) = ax.plot(poly_xs, poly_ys, color="red", lw=2, zorder=5)

step_label = ax.text(
    0.02,
    0.02,
    "Исходная фигура",
    transform=ax.transAxes,
    fontsize=9,
    va="bottom",
    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
)

ax.set_title(
    "Алгоритм XOR",
    fontsize=11,
    fontweight="bold",
)
ax.legend(loc="upper right", fontsize=9)

LABELS = {
    "pre": "Исходная фигура",
    "outline": "Растеризованный контур рёбер",
    "done": "Заливка завершена (контур восстановлен)",
}


def update(fi):
    g, ftype, last_row = anim_frames[fi]
    im.set_data(g)

    if ftype == "pre":
        step_label.set_text(LABELS["pre"])
        border_scatter.set_alpha(0.0)
        hline.set_alpha(0.0)

    elif ftype == "outline":
        step_label.set_text(LABELS["outline"])
        border_scatter.set_alpha(0.7)  # показываем растр-пиксели контура
        hline.set_alpha(0.0)

    elif ftype == "fill":
        border_scatter.set_alpha(0.0)
        hline.set_ydata([last_row, last_row])
        hline.set_alpha(0.85)

    elif ftype == "done":
        step_label.set_text(LABELS["done"])
        border_scatter.set_alpha(0.0)
        hline.set_alpha(0.0)

    return [im, border_scatter, hline, step_label]


ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(anim_frames),
    interval=120,
    blit=True,
    repeat=True,
    repeat_delay=600,
)

plt.tight_layout()
plt.show()
