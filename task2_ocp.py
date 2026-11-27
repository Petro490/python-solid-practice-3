"""
Задача 2. Принцип открытости/закрытости (OCP).

Что было не так в исходном коде:
    DiscountCalculator.calculate_discount перебирал типы клиентов через
    if/elif. Каждый новый тип клиента (например, PremiumCustomer) требовал
    правки ЭТОГО ЖЕ метода, то есть класс был закрыт для расширения и
    открыт для изменения — ровно наоборот тому, чего требует OCP.

Что сделано:
    * Customer — абстрактный базовый класс с методом calculate_discount();
    * RegularCustomer, VIPCustomer, NewCustomer — наследники со своей формулой;
    * DiscountCalculator больше не знает про типы клиентов, он просто
      вызывает полиморфный метод;
    * PremiumCustomer добавлен как демонстрация: новый класс — и всё,
      существующий код менять не нужно.
"""

from abc import ABC, abstractmethod


class Customer(ABC):
    """Клиент интернет-магазина.

    Базовый класс задаёт общий контракт: у любого клиента можно спросить
    скидку на сумму заказа. Конкретную формулу знают только наследники.
    """

    #: Ставка скидки (0.15 = 15%). У каждого наследника своя.
    discount_rate = 0.0

    #: Название категории — только для красивого вывода в демонстрации.
    title = "Клиент"

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calculate_discount(self, order_total):
        """Вернуть сумму скидки для заказа на order_total рублей."""
        # Абстрактный метод заставляет каждого наследника определить свою логику.
        raise NotImplementedError

    def total_with_discount(self, order_total):
        """Сумма к оплате с учётом скидки (общая логика для всех клиентов)."""
        # Эта логика одинакова для всех, поэтому её не нужно дублировать.
        return order_total - self.calculate_discount(order_total)

    def __str__(self):
        return f"{self.title} «{self.name}»"


class RegularCustomer(Customer):
    """Постоянный клиент — 5%."""
    discount_rate = 0.05
    title = "Постоянный клиент"

    def calculate_discount(self, order_total):
        return order_total * self.discount_rate


class VIPCustomer(Customer):
    """VIP-клиент — 15%."""
    discount_rate = 0.15
    title = "VIP-клиент"

    def calculate_discount(self, order_total):
        return order_total * self.discount_rate


class NewCustomer(Customer):
    """Новый клиент — 2%."""
    discount_rate = 0.02
    title = "Новый клиент"

    def calculate_discount(self, order_total):
        return order_total * self.discount_rate


class PremiumCustomer(Customer):
    """НОВЫЙ тип клиента — 25%.

    Добавлен БЕЗ изменения Customer и DiscountCalculator: достаточно
    создать наследника и реализовать метод. Это и есть проверка OCP.
    """
    discount_rate = 0.25
    title = "Premium-клиент"

    def calculate_discount(self, order_total):
        return order_total * self.discount_rate


class DiscountCalculator:
    """Расчёт скидки. Не зависит от конкретных типов клиентов.

    Класс работает только с абстракцией Customer, поэтому новые категории
    клиентов не требуют его правки. Проверок isinstance/if-elif здесь нет.
    """

    def calculate_discount(self, customer, order_total):
        """Скидка для клиента — делегируем самому клиенту (полиморфизм)."""
        if order_total < 0:
            raise ValueError("Сумма заказа не может быть отрицательной")
        return customer.calculate_discount(order_total)

    def calculate_total(self, customer, order_total):
        """Итоговая сумма к оплате."""
        return order_total - self.calculate_discount(customer, order_total)


def demo():
    """Демонстрация работы решения по задаче 2."""
    print("=" * 60)
    print("Задача 2. OCP: типы клиентов через наследование")
    print("=" * 60)

    customers = [
        NewCustomer("Анна"),
        RegularCustomer("Игорь"),
        VIPCustomer("Мария"),
        PremiumCustomer("Олег"),
    ]
    order_total = 10_000
    calculator = DiscountCalculator()

    print(f"\nСумма заказа: {order_total} руб.\n")
    print(f"{'Клиент':<32}{'Скидка, %':>10}{'Скидка, ₽':>12}{'К оплате, ₽':>14}")
    print("-" * 68)
    for customer in customers:
        discount = calculator.calculate_discount(customer, order_total)
        total = calculator.calculate_total(customer, order_total)
        print(
            f"{str(customer):<32}"
            f"{customer.discount_rate * 100:>10.0f}"
            f"{discount:>12.2f}"
            f"{total:>14.2f}"
        )

    print(
        "\nPremiumCustomer добавлен новым классом — "
        "DiscountCalculator не менялся."
    )


if __name__ == "__main__":
    demo()
