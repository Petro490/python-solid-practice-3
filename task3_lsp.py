"""
Задача 3. Принцип подстановки Лисков (LSP).

Что было не так в исходном коде:
    Square наследовался от Rectangle, но переопределял set_width/set_height
    так, что менялись ОБА размера. Из-за этого объект Square нельзя было
    подставить вместо Rectangle: функция, которая ставит прямоугольнику
    ширину 5 и высоту 4 и ждёт площадь 20, получала бы 16. Наследование
    выглядело логичным («квадрат — частный случай прямоугольника»), но
    нарушало контракт базового класса.

Что сделано:
    * Shape — абстрактный базовый класс с методом area();
    * Rectangle и Square — независимые наследники Shape, друг от друга
      не наследуются;
    * у Rectangle есть изменяемые ширина/высота, у Square — только сторона;
    * в конце файла тестовая функция, которая принимает Shape и проверяет,
      что подстановка любого наследника работает корректно.

Плюс: убрано прямое обращение к _width/_height из наследника — размеры
меняются через свойства, поэтому валидация работает для всех фигур.
"""

from abc import ABC, abstractmethod


class Shape(ABC):
    """Геометрическая фигура. Контракт: у любой фигуры можно узнать площадь."""

    @abstractmethod
    def area(self):
        """Площадь фигуры."""
        raise NotImplementedError

    def __str__(self):
        # Общее поведение для всех фигур — не требует переопределения.
        return f"{type(self).__name__}, площадь = {self.area():.2f}"


class Rectangle(Shape):
    """Прямоугольник с независимыми шириной и высотой."""

    def __init__(self, width, height):
        # Валидацию делает сеттер, поэтому проверка одна для всех способов задания.
        self.width = width
        self.height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        # Свойство (property) защищает инвариант: размер всегда положительный.
        if width <= 0:
            raise ValueError("Ширина должна быть больше нуля")
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        if height <= 0:
            raise ValueError("Высота должна быть больше нуля")
        self._height = height

    def area(self):
        return self.width * self.height


class Square(Shape):
    """Квадрат. Отдельный наследник Shape, а НЕ наследник Rectangle.

    Именно поэтому у него нет методов set_width/set_height, которые могли бы
    нарушить контракт прямоугольника: сторона одна, и она одна и меняется.
    """

    def __init__(self, size):
        self.size = size

    @property
    def size(self):
        return self._side

    @size.setter
    def size(self, size):
        if size <= 0:
            raise ValueError("Сторона квадрата должна быть больше нуля")
        self._side = size

    def area(self):
        return self.size ** 2


def print_area(shape):
    """Функция, работающая с ЛЮБОЙ фигурой (проверка принципа подстановки).

    Она не знает, прямоугольник перед ней или квадрат, — и это правильно:
    любой наследник Shape можно подставить без изменения кода функции.
    """
    # Явная проверка типа не обязательна для работы, но делает контракт наглядным.
    if not isinstance(shape, Shape):
        raise TypeError("Ожидался объект Shape")
    return shape.area()


def test_lsp():
    """Тестовая функция: проверяем ожидаемые площади и подстановку фигур."""
    # Список фигур разного типа — единая точка проверки.
    cases = [
        (Rectangle(3, 4), 12),   # площадь прямоугольника 3x4
        (Rectangle(5, 2), 10),
        (Square(5), 25),         # площадь квадрата со стороной 5
        (Square(1), 1),
    ]

    for shape, expected in cases:
        actual = print_area(shape)
        assert abs(actual - expected) < 1e-9, (
            f"{shape}: ожидалось {expected}, получено {actual}"
        )
        print(f"  OK  {shape}")

    # Ключевая проверка LSP: смена размеров прямоугольника не задевает
    # «квадратные» правила — у каждой фигуры своя независимая модель.
    rectangle = Rectangle(2, 3)
    rectangle.width = 5
    rectangle.height = 4
    assert rectangle.area() == 20, "Прямоугольник должен иметь площадь 20"
    print("  OK  Rectangle(2,3) после width=5, height=4 -> площадь 20")

    square = Square(2)
    square.size = 5
    assert square.area() == 25, "Квадрат должен иметь площадь 25"
    print("  OK  Square(2) после size=5 -> площадь 25")

    # Проверяем защиту инварианта (отрицательные размеры запрещены).
    try:
        Square(-1)
    except ValueError:
        print("  OK  Square(-1) отклонён с ValueError")
    else:
        raise AssertionError("Отрицательная сторона должна вызывать ValueError")


def demo():
    """Запуск демонстрации и тестов по задаче 3."""
    print("=" * 60)
    print("Задача 3. LSP: Shape -> Rectangle / Square")
    print("=" * 60)

    shapes = [Rectangle(3, 4), Square(5), Rectangle(10, 0.5), Square(2)]
    print("\nОбщий цикл по фигурам (функция принимает Shape):")
    for shape in shapes:
        print(f"  {shape}")

    print("\nТесты подстановки:")
    test_lsp()
    print("\nВсе проверки LSP пройдены.")


if __name__ == "__main__":
    demo()
