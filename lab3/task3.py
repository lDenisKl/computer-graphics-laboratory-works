import matplotlib.pyplot as plt
import numpy as np


def bresenham_line(x0: int, y0: int, x1: int, y1: int):
    """Алгоритм Брезенхема растеризации отрезка"""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return points


def plot_bresenham_line(x0, y0, x1, y1):
    points = bresenham_line(x0, y0, x1, y1)

    fig, ax = plt.subplots(figsize=(11, 9))

    min_x = min(x0, x1) - 1
    max_x = max(x0, x1) + 2
    min_y = min(y0, y1) - 1
    max_y = max(y0, y1) + 2

    ax.set_xticks(np.arange(min_x, max_x))
    ax.set_yticks(np.arange(min_y, max_y))
    ax.grid(True, color="gray", linestyle="-", linewidth=0.8, alpha=0.7)

    ax.plot([x0, x1], [y0, y1], "b-", linewidth=3, label="Стандартный метод")

    # отмеченные пиксели
    px, py = zip(*points)
    ax.scatter(
        px,
        py,
        color="red",
        s=220,
        marker="s",
        edgecolors="black",
        linewidth=1.5,
        label="Пиксели по алгоритму Брезенхема",
        zorder=5,
    )

    for x, y in points:
        ax.text(
            x,
            y + 0.15,
            f"({x},{y})",
            fontsize=9,
            ha="center",
            va="bottom",
            color="darkred",
        )

    ax.set_title(
        "Алгоритм Брезенхема растеризации отрезка",
        fontsize=14,
    )
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_aspect("equal")
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.show()
    print(points)


def bresenham_circle(cx: int, cy: int, r: int):
    """Алгоритм Брезенхема растеризации окружности"""
    points = []
    x = 0
    y = r
    d = 3 - 2 * r

    while x <= y:
        for dx, dy in [
            (x, y),
            (-x, y),
            (x, -y),
            (-x, -y),
            (y, x),
            (-y, x),
            (y, -x),
            (-y, -x),
        ]:
            points.append((cx + dx, cy + dy))
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1

    return list(set(points))


def plot_bresenham_circle(cx, cy, r):
    """Визуализация второй части лабораторной"""
    points = bresenham_circle(cx, cy, r)

    fig, ax = plt.subplots(figsize=(11, 10))

    min_coord = min(cx - r - 1, cy - r - 1)
    max_coord = max(cx + r + 2, cy + r + 2)
    ax.set_xticks(np.arange(min_coord, max_coord))
    ax.set_yticks(np.arange(min_coord, max_coord))
    ax.grid(True, color="gray", linestyle="-", linewidth=0.8, alpha=0.7)

    circle_standard = plt.Circle(
        (cx, cy), r, fill=False, color="blue", linewidth=3, label="Стандартный метод"
    )
    ax.add_patch(circle_standard)

    # отмеченные пиксели
    px, py = zip(*points)
    ax.scatter(
        px,
        py,
        color="red",
        s=180,
        marker="s",
        edgecolors="black",
        linewidth=1.5,
        label="Пиксели по алгоритму Брезенхема",
        zorder=5,
    )

    ax.set_title(
        "Алгоритм Брезенхема растеризации окружности",
        fontsize=14,
    )
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_aspect("equal")
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.show()
    print(f"Количество пикселей: {len(points)}")


if __name__ == "__main__":

    print("\nПервая часть — отрезок:")
    print("Введите координаты отрезка: ")
    x0, y0, x1, y1 = map(int, input("x0 y0 x1 y1 → ").split())

    plot_bresenham_line(x0, y0, x1, y1)

    print("\nВторая часть — окружность:")

    print("Введите координаты центра и радиус: ")

    g = list(map(int, input().split()))
    plot_bresenham_circle(g[0], g[1], g[2])
