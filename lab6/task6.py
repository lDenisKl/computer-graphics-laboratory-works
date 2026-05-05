import math
from itertools import combinations

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MplPolygon

# ── Точки ────────────────────────────────────────────────────────────────────
np.random.seed(42)
N = 14
POINTS = [tuple(map(float, p)) for p in np.random.uniform(60, 440, (N, 2))]


# ── Геометрия ─────────────────────────────────────────────────────────────────


def cross2d(O, A, B):
    return (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0])


def point_in_triangle(p, a, b, c):
    if abs(cross2d(a, b, c)) < 1e-9:
        return False
    d1, d2, d3 = cross2d(a, b, p), cross2d(b, c, p), cross2d(c, a, p)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


def brute_force_hull(pts):
    n = len(pts)
    first_elim = {}
    for i, j, k in combinations(range(n), 3):
        for l in range(n):
            if l in (i, j, k) or l in first_elim:
                continue
            if point_in_triangle(pts[l], pts[i], pts[j], pts[k]):
                first_elim[l] = (i, j, k)
    hull = [i for i in range(n) if i not in first_elim]
    cx = sum(pts[i][0] for i in hull) / len(hull)
    cy = sum(pts[i][1] for i in hull) / len(hull)
    hull.sort(key=lambda i: math.atan2(pts[i][1] - cy, pts[i][0] - cx))
    return hull, first_elim, (cx, cy)


hull, first_elim, centroid = brute_force_hull(POINTS)
N_PTS = len(POINTS)


# ── Кадры ────────────────────────────────────────────────────────────────────

keyframes = []

keyframes.append(
    dict(
        label="Все точки — кандидаты в крайние",
        elim=[],
        current=[],
        tri=None,
        show_hull=False,
        show_sort=False,
    )
)

# Группируем по треугольнику в порядке обхода combinations,
# чтобы один кадр = один треугольник → все точки внутри него сразу
tri_to_pts = {}
for l, tri in first_elim.items():
    tri_to_pts.setdefault(tri, []).append(l)

elim_so_far = []
for tri in combinations(range(N_PTS), 3):
    if tri not in tri_to_pts:
        continue
    pts_elim = sorted(tri_to_pts[tri])
    elim_so_far = elim_so_far + pts_elim
    i, j, k = tri
    pts_str = ", ".join(str(p) for p in pts_elim)
    keyframes.append(
        dict(
            label=f"△{i}–{j}–{k}: точки {pts_str} — не крайние",
            elim=list(elim_so_far),
            current=pts_elim,
            tri=tri,
            show_hull=False,
            show_sort=False,
        )
    )

keyframes.append(
    dict(
        label=f"Крайних: {len(hull)}  |  устранено: {len(first_elim)}",
        elim=list(elim_so_far),
        current=[],
        tri=None,
        show_hull=False,
        show_sort=False,
    )
)
keyframes.append(
    dict(
        label="Сортировка по полярному углу",
        elim=list(elim_so_far),
        current=[],
        tri=None,
        show_hull=True,
        show_sort=True,
    )
)
keyframes.append(
    dict(
        label=f"Выпуклая оболочка  —  {len(hull)} вершин",
        elim=list(elim_so_far),
        current=[],
        tri=None,
        show_hull=True,
        show_sort=False,
    )
)

HOLD = 40
anim_frames = [kf for kf in keyframes for _ in range(HOLD)]


# ── Фигура ────────────────────────────────────────────────────────────────────

all_x, all_y = [p[0] for p in POINTS], [p[1] for p in POINTS]
PAD = 40
XLIM = (min(all_x) - PAD, max(all_x) + PAD)
YLIM = (min(all_y) - PAD, max(all_y) + PAD)

fig, ax = plt.subplots(figsize=(8, 7))
ax.set_aspect("equal")
ax.set_xlim(XLIM)
ax.set_ylim(YLIM)
ax.grid(True, alpha=0.22)
ax.set_title(
    "Алгоритм полного перебора выпуклой оболочки",
    fontsize=10,
    fontweight="bold",
)

# Анимируемые артисты
sc_blue = ax.scatter([], [], c="#1565C0", s=65, zorder=4)
sc_gray = ax.scatter([], [], c="#9E9E9E", s=45, alpha=0.6, zorder=3)
sc_red = ax.scatter([], [], c="red", s=200, marker="x", linewidths=3, zorder=5)
sc_cen = ax.scatter([], [], c="purple", s=150, marker="+", linewidths=2.5, zorder=6)

tri_patch = MplPolygon(
    [[0, 0], [1, 0], [0, 1]],
    closed=True,
    fc="#FFE0B2",
    ec="#E65100",
    alpha=0.6,
    lw=1.8,
    visible=False,
    zorder=1,
)
ax.add_patch(tri_patch)

(hull_line,) = ax.plot([], [], "-", color="#1565C0", lw=2.5, zorder=3)
rays = LineCollection([], colors="purple", lw=0.9, ls="--", alpha=0.5, zorder=2)
ax.add_collection(rays)

# Метки порядка обхода (на вершинах оболочки)
order_texts = [
    ax.text(
        *POINTS[idx],
        "",
        fontsize=8,
        color="#1565C0",
        fontweight="bold",
        ha="right",
        va="bottom",
        zorder=8,
    )
    for idx in hull
]

info = ax.text(
    0.02,
    0.02,
    "",
    transform=ax.transAxes,
    fontsize=10,
    va="bottom",
    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.88),
    zorder=9,
)

# Статичные номера точек (часть фона)
for i, (x, y) in enumerate(POINTS):
    ax.annotate(
        str(i), (x, y), xytext=(5, 5), textcoords="offset points", fontsize=8, zorder=7
    )

ax.legend(
    handles=[
        Line2D([0], [0], marker="o", color="w", mfc="#1565C0", ms=9, label="Крайняя"),
        Line2D([0], [0], marker="o", color="w", mfc="#9E9E9E", ms=9, label="Устранена"),
        Line2D([0], [0], marker="x", color="red", ms=10, mew=3, lw=0, label="Текущая"),
    ],
    loc="upper right",
    fontsize=9,
)


# ── Обновление кадра ─────────────────────────────────────────────────────────


def _off(lst):
    return np.array(lst) if lst else np.empty((0, 2))


def update(fi):
    kf = anim_frames[fi]
    elim_set = set(kf["elim"])
    cur = kf["current"]

    cur_set = set(cur) if cur else set()
    sc_blue.set_offsets(_off([POINTS[i] for i in range(N_PTS) if i not in elim_set]))
    sc_gray.set_offsets(_off([POINTS[i] for i in elim_set if i not in cur_set]))
    sc_red.set_offsets(_off([POINTS[i] for i in cur_set]))

    if kf["tri"]:
        i, j, k = kf["tri"]
        tri_patch.set_xy([POINTS[i], POINTS[j], POINTS[k]])
        tri_patch.set_visible(True)
    else:
        tri_patch.set_visible(False)

    if kf["show_hull"]:
        hx = [POINTS[i][0] for i in hull] + [POINTS[hull[0]][0]]
        hy = [POINTS[i][1] for i in hull] + [POINTS[hull[0]][1]]
        hull_line.set_data(hx, hy)
    else:
        hull_line.set_data([], [])

    if kf["show_sort"]:
        cx, cy = centroid
        rays.set_segments([[(cx, cy), POINTS[i]] for i in hull])
        sc_cen.set_offsets([[cx, cy]])
    else:
        rays.set_segments([])
        sc_cen.set_offsets(np.empty((0, 2)))

    for t, order, idx in zip(order_texts, range(1, len(hull) + 1), hull):
        t.set_text(f"({order})" if kf["show_hull"] else "")

    info.set_text(kf["label"])

    return [
        sc_blue,
        sc_gray,
        sc_red,
        sc_cen,
        tri_patch,
        hull_line,
        rays,
        info,
    ] + order_texts


ani = animation.FuncAnimation(
    fig,
    update,
    frames=len(anim_frames),
    interval=50,
    blit=True,
    repeat=True,
    repeat_delay=1200,
)

plt.tight_layout()
plt.show()
