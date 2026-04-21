import json
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.lines import Line2D

with open("data.json", encoding="utf-8") as f:
    d = json.load(f)

polygon = [tuple(p) for p in d["polygon"]]
P1 = tuple(d["segment"]["p1"])
P2 = tuple(d["segment"]["p2"])
r = d["rectangle"]
xmin, ymin, xmax, ymax = r["xmin"], r["ymin"], r["xmax"], r["ymax"]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def ensure_ccw(poly):
    area = sum(
        poly[i][0] * poly[(i + 1) % len(poly)][1]
        - poly[(i + 1) % len(poly)][0] * poly[i][1]
        for i in range(len(poly))
    )
    return poly[::-1] if area < 0 else poly


def rect_intersections(p1, p2):
    D = (p2[0] - p1[0], p2[1] - p1[1])
    pts = []
    for a, b in [
        ((xmin, ymin), (xmax, ymin)),
        ((xmax, ymin), (xmax, ymax)),
        ((xmax, ymax), (xmin, ymax)),
        ((xmin, ymax), (xmin, ymin)),
    ]:
        N = (-(b[1] - a[1]), b[0] - a[0])
        den = dot(N, D)
        if den == 0:
            continue
        t = dot(N, (a[0] - p1[0], a[1] - p1[1])) / den
        p = (p1[0] + t * D[0], p1[1] + t * D[1])
        ex, ey = sorted([a[0], b[0]]), sorted([a[1], b[1]])
        if (
            ex[0] - 1e-9 <= p[0] <= ex[1] + 1e-9
            and ey[0] - 1e-9 <= p[1] <= ey[1] + 1e-9
            and 0 <= t <= 1
        ):
            pts.append(p)
    return pts


def cyrus_beck(p1, p2, poly):
    poly = ensure_ccw(poly)
    D = (p2[0] - p1[0], p2[1] - p1[1])
    tE, tL, pe, pl = 0.0, 1.0, [], []
    for i in range(len(poly)):
        A, B = poly[i], poly[(i + 1) % len(poly)]
        N = (-(B[1] - A[1]), B[0] - A[0])
        den = dot(N, D)
        if den == 0:
            if dot(N, (A[0] - p1[0], A[1] - p1[1])) < 0:
                return None
            continue
        t = dot(N, (A[0] - p1[0], A[1] - p1[1])) / den
        p = (p1[0] + t * D[0], p1[1] + t * D[1])
        if den < 0:
            pl.append(p)
            tL = min(tL, t)
        else:
            pe.append(p)
            tE = max(tE, t)
    if tE > tL:
        return None
    return (
        (p1[0] + tE * D[0], p1[1] + tE * D[1]),
        (p1[0] + tL * D[0], p1[1] + tL * D[1]),
        pe,
        pl,
    )


def cohen_sutherland(p1, p2):
    def code(x, y):
        c = 0
        if x < xmin:
            c |= 1
        elif x > xmax:
            c |= 2
        if y < ymin:
            c |= 4
        elif y > ymax:
            c |= 8
        return c

    x1, y1, x2, y2 = float(p1[0]), float(p1[1]), float(p2[0]), float(p2[1])
    c1, c2 = code(x1, y1), code(x2, y2)
    while True:
        if not (c1 | c2):
            return (x1, y1), (x2, y2)
        if c1 & c2:
            return None
        co = c1 or c2
        if co & 8:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif co & 4:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif co & 2:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        else:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin
        if co == c1:
            x1, y1 = x, y
            c1 = code(x1, y1)
        else:
            x2, y2 = x, y
            c2 = code(x2, y2)


def midpoint_clip(p1, p2, iters=52):
    def inside(x, y):
        return xmin <= x <= xmax and ymin <= y <= ymax

    def code(x, y):
        c = 0
        if x < xmin:
            c |= 1
        elif x > xmax:
            c |= 2
        if y < ymin:
            c |= 4
        elif y > ymax:
            c |= 8
        return c

    x1, y1, x2, y2 = float(p1[0]), float(p1[1]), float(p2[0]), float(p2[1])
    in1, in2 = inside(x1, y1), inside(x2, y2)
    if in1 and in2:
        return (x1, y1), (x2, y2)
    if code(x1, y1) & code(x2, y2):
        return None

    def bisect(ox, oy, ix, iy):
        for _ in range(iters):
            mx, my = (ox + ix) / 2, (oy + iy) / 2
            if inside(mx, my):
                ix, iy = mx, my
            else:
                ox, oy = mx, my
        return (ox + ix) / 2, (oy + iy) / 2

    nx1, ny1 = bisect(x1, y1, x2, y2) if not in1 else (x1, y1)
    nx2, ny2 = bisect(x2, y2, x1, y1) if not in2 else (x2, y2)
    return (nx1, ny1), (nx2, ny2)


def seg(ax, a, b, **kw):
    ax.plot([a[0], b[0]], [a[1], b[1]], **kw)


def mark(ax, p, label="", **kw):
    ax.scatter(p[0], p[1], zorder=5, **kw)
    if label:
        ax.annotate(
            label,
            p,
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
            fontweight="bold",
        )


def extend_line(ax, a, b, **kw):
    xl, yl = ax.get_xlim(), ax.get_ylim()
    dx, dy = b[0] - a[0], b[1] - a[1]
    ts = ([(xl[0] - a[0]) / dx, (xl[1] - a[0]) / dx] if dx else [-1e9, 1e9]) + (
        [(yl[0] - a[1]) / dy, (yl[1] - a[1]) / dy] if dy else [-1e9, 1e9]
    )
    ts.sort()
    t1, t2 = ts[1], ts[2]
    ax.plot([a[0] + t1 * dx, a[0] + t2 * dx], [a[1] + t1 * dy, a[1] + t2 * dy], **kw)


fig, axes = plt.subplots(1, 3, figsize=(18, 7))

all_x = [P1[0], P2[0], xmin, xmax] + [p[0] for p in polygon]
all_y = [P1[1], P2[1], ymin, ymax] + [p[1] for p in polygon]
pad = 40
lx = (min(all_x) - pad, max(all_x) + pad)
ly = (min(all_y) - pad, max(all_y) + pad)

for ax in axes:
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(lx)
    ax.set_ylim(ly)

# 1. Сайрус–Бек
ax = axes[0]
poly = ensure_ccw(polygon)
for i in range(len(poly)):
    extend_line(
        ax,
        poly[i],
        poly[(i + 1) % len(poly)],
        color="steelblue",
        lw=0.8,
        ls="--",
        alpha=0.5,
    )
ax.add_patch(
    MplPolygon(
        poly,
        closed=True,
        edgecolor="steelblue",
        facecolor="lightblue",
        alpha=0.3,
        lw=1.5,
    )
)
seg(ax, P1, P2, color="gray", lw=1, ls=":")
mark(ax, P1, "P₁", color="gray", s=40)
mark(ax, P2, "P₂", color="gray", s=40)
res = cyrus_beck(P1, P2, polygon)
if res:
    q1, q2, pe, pl = res
    seg(ax, P1, q1, color="gray", lw=1.5, ls="--")
    seg(ax, q2, P2, color="gray", lw=1.5, ls="--")
    seg(ax, q1, q2, color="green", lw=3, zorder=3)
    for i, p in enumerate(pe):
        mark(ax, p, f"PE{i+1}", color="red", s=50)
    for i, p in enumerate(pl):
        mark(ax, p, f"PL{i+1}", color="orange", s=50)
    # mark(ax, q1, "Q₁", color="green", s=100, marker="D")
    # mark(ax, q2, "Q₂", color="green", s=100, marker="D")
    ax.set_title(
        f"Сайрус–Бек\nQ₁=({q1[0]:.1f},{q1[1]:.1f})  Q₂=({q2[0]:.1f},{q2[1]:.1f})",
        fontsize=9,
    )
else:
    ax.set_title("Сайрус–Бек\nОтрезок полностью невидим", fontsize=9, color="red")

# 2. Коэн–Сазерленд
ax = axes[1]
ax.axvline(xmin, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.axvline(xmax, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.axhline(ymin, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.axhline(ymax, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.add_patch(
    MplPolygon(
        [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)],
        closed=True,
        edgecolor="steelblue",
        facecolor="lightblue",
        alpha=0.3,
        lw=1.5,
    )
)
seg(ax, P1, P2, color="gray", lw=1, ls=":")
mark(ax, P1, "P₁", color="gray", s=40)
mark(ax, P2, "P₂", color="gray", s=40)
res = cohen_sutherland(P1, P2)
if res:
    q1, q2 = res
    seg(ax, P1, q1, color="gray", lw=1.5, ls="--")
    seg(ax, q2, P2, color="gray", lw=1.5, ls="--")
    seg(ax, q1, q2, color="green", lw=3, zorder=3)
    for i, p in enumerate(rect_intersections(P1, P2)):
        mark(ax, p, f"P{i+1}'", color="red" if i == 0 else "orange", s=50)
    # mark(ax, q1, "Q₁", color="green", s=100, marker="D")
    # mark(ax, q2, "Q₂", color="green", s=100, marker="D")
    ax.set_title(
        f"Коэн–Сазерленд\nQ₁=({q1[0]:.1f},{q1[1]:.1f})  Q₂=({q2[0]:.1f},{q2[1]:.1f})",
        fontsize=9,
    )
else:
    ax.set_title("Коэн–Сазерленд\nОтрезок полностью невидим", fontsize=9, color="red")

# 3. Средней точки
ax = axes[2]
ax.axvline(xmin, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.axvline(xmax, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.axhline(ymin, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.axhline(ymax, color="steelblue", lw=0.8, ls="--", alpha=0.5)
ax.add_patch(
    MplPolygon(
        [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)],
        closed=True,
        edgecolor="steelblue",
        facecolor="lightblue",
        alpha=0.3,
        lw=1.5,
    )
)
seg(ax, P1, P2, color="gray", lw=1, ls=":")
mark(ax, P1, "P₁", color="gray", s=40)
mark(ax, P2, "P₂", color="gray", s=40)
res = midpoint_clip(P1, P2)
if res:
    q1, q2 = res
    seg(ax, P1, q1, color="gray", lw=1.5, ls="--")
    seg(ax, q2, P2, color="gray", lw=1.5, ls="--")
    seg(ax, q1, q2, color="green", lw=3, zorder=3)
    for i, p in enumerate(rect_intersections(P1, P2)):
        mark(ax, p, f"P{i+1}'", color="red" if i == 0 else "orange", s=50)
    # mark(ax, q1, "Q₁", color="green", s=100, marker="D")
    # mark(ax, q2, "Q₂", color="green", s=100, marker="D")
    ax.set_title(
        f"Средней точки\nQ₁=({q1[0]:.1f},{q1[1]:.1f})  Q₂=({q2[0]:.1f},{q2[1]:.1f})",
        fontsize=9,
    )
else:
    ax.set_title("Средней точки\nОтрезок полностью невидим", fontsize=9, color="red")

fig.legend(
    handles=[
        Line2D([0], [0], color="gray", lw=1, ls=":", label="P₁, P₂ — концы отрезка"),
        Line2D([0], [0], color="gray", lw=1.5, ls="--", label="Невидимая часть"),
        Line2D([0], [0], color="green", lw=3, ls="-", label="Видимая часть"),
        Line2D([0], [0], color="steelblue", lw=1, ls="--", label="Линии окна"),
        Line2D(
            [0],
            [0],
            color="red",
            marker="o",
            lw=0,
            ms=8,
            label="PE — потенц. точки входа",
        ),
        Line2D(
            [0],
            [0],
            color="orange",
            marker="o",
            lw=0,
            ms=8,
            label="PL — потенц. точки выхода",
        ),
        Line2D(
            [0],
            [0],
            color="green",
            marker="D",
            lw=0,
            ms=8,
            label="Q₁, Q₂ — итоговые точки отсечения",
        ),
    ],
    loc="lower center",
    ncol=4,
    fontsize=9,
    bbox_to_anchor=(0.5, -0.07),
)

plt.tight_layout()
plt.show()
