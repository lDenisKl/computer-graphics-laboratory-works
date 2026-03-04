import math


# Задача 1. Даны точки A, B, C, D. Определить взаимное расположение прямых AB и CD
# (пересекаются, не пересекаются, совпадают)
def line_intersection(A, B, C, D):
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C
    x4, y4 = D

    AB = (x2 - x1, y2 - y1)
    CD = (x4 - x3, y4 - y3)

    det = AB[0] * CD[1] - AB[1] * CD[0]

    if abs(det) > 1e-9:
        return "пересекаются"

    AC = (x3 - x1, y3 - y1)
    det2 = AB[0] * AC[1] - AB[1] * AC[0]

    if abs(det2) < 1e-9:
        return "совпадают"
    else:
        return "параллельные"


# Задача 2. Даны три точки А,В,С, лежащие на одной прямой. Определить расположение точки С
# относительно луча АВ
def point_on_ray(A, B, C):
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C

    AB = (x2 - x1, y2 - y1)
    AC = (x3 - x1, y3 - y1)

    dot = AB[0] * AC[0] + AB[1] * AC[1]

    if abs(dot) < 1e-9:
        return "С совп с А"
    elif dot > 0:
        return "С на луче"
    else:
        return "С не на луче"


# Задача 3. Даны три точки А,В,С, определить является ли обход А-В-С обходом по часовой
# стрелке или против (точки заданы на плоскости).
def orientation(A, B, C):
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C

    val = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)

    if abs(val) < 1e-9:
        return "коллинеарные"
    elif val > 0:
        return "против часовой"
    else:
        return "по часовой"


# Задача 4.Определить принадлежит ли данная точка прямой, заданной двумя
# плоскостями. Плоскости заданы своими коэффициентами.
def point_on_line_from_planes(plane1, plane2, M, eps=1e-9):
    A1, B1, C1, D1 = plane1
    A2, B2, C2, D2 = plane2
    x, y, z = M

    res1 = A1 * x + B1 * y + C1 * z + D1
    res2 = A2 * x + B2 * y + C2 * z + D2

    return abs(res1) < eps and abs(res2) < eps


def input_point_2d(prompt):
    """Запрашивает у пользователя координаты точки на плоскости (x y)."""
    while True:
        try:
            coords = input(prompt).strip().split()
            if len(coords) != 2:
                raise ValueError("Необходимо ввести два числа")
            x, y = map(float, coords)
            return (x, y)
        except ValueError as e:
            print(f"Ошибка ввода: {e}. Попробуйте снова.")


def input_point_3d(prompt):
    """Запрашивает у пользователя координаты точки в пространстве (x y z)."""
    while True:
        try:
            coords = input(prompt).strip().split()
            if len(coords) != 3:
                raise ValueError("Необходимо ввести три числа")
            x, y, z = map(float, coords)
            return (x, y, z)
        except ValueError as e:
            print(f"Ошибка ввода: {e}. Попробуйте снова.")


def input_plane(prompt):
    """Запрашивает у пользователя коэффициенты плоскости A B C D."""
    while True:
        try:
            coeffs = input(prompt).strip().split()
            if len(coeffs) != 4:
                raise ValueError("Необходимо ввести четыре числа")
            A, B, C, D = map(float, coeffs)
            return (A, B, C, D)
        except ValueError as e:
            print(f"Ошибка ввода: {e}. Попробуйте снова.")


def main():

    while True:
        print("\nВыберите задачу:")
        print("0 - Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            break

        elif choice == "1":
            A = input_point_2d("Введите координаты точки A (x y): ")
            B = input_point_2d("Введите координаты точки B (x y): ")
            C = input_point_2d("Введите координаты точки C (x y): ")
            D = input_point_2d("Введите координаты точки D (x y): ")
            result = line_intersection(A, B, C, D)
            print(f"Результат: {result}")

        elif choice == "2":
            A = input_point_2d("Введите координаты точки A (x y) - начало луча: ")
            B = input_point_2d("Введите координаты точки B (x y) - направление луча: ")
            C = input_point_2d("Введите координаты точки C (x y): ")
            result = point_on_ray(A, B, C)
            print(f"Результат: {result}")

        elif choice == "3":
            A = input_point_2d("Введите координаты точки A (x y): ")
            B = input_point_2d("Введите координаты точки B (x y): ")
            C = input_point_2d("Введите координаты точки C (x y): ")
            result = orientation(A, B, C)
            print(f"Результат: {result}")

        elif choice == "4":
            print(
                "Введите коэффициенты плоскостей в виде A B C D (уравнение: Ax+By+Cz+D=0)"
            )
            plane1 = input_plane("Коэффициенты первой плоскости: ")
            plane2 = input_plane("Коэффициенты второй плоскости: ")
            M = input_point_3d("Введите координаты точки M (x y z): ")
            result = point_on_line_from_planes(plane1, plane2, M)
            if result:
                print("Точка принадлежит прямой.")
            else:
                print("Точка НЕ принадлежит прямой.")

        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    main()
