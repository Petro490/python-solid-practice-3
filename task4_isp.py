"""
Задача 4. Принцип разделения интерфейса (ISP).

Что было не так в исходном коде:
    MultiFunctionDevice объявлял сразу четыре метода (печать, сканирование,
    факс, копирование). Класс SimplePrinter был обязан реализовать все четыре,
    хотя умеет только печатать, и три метода вынужденно выбрасывали
    NotImplementedError. Клиент такого класса не мог доверять интерфейсу:
    метод есть, но вызвать его нельзя.

Что сделано:
    * вместо одного «толстого» интерфейса — четыре узких:
      Printable, Scannable, Faxable, Copyable;
    * каждое устройство наследует только те интерфейсы, которые реально
      поддерживает;
    * «лишних» методов с NotImplementedError в конкретных классах больше нет —
      если устройство не сканирует, у него просто нет метода scan_document().

Проверка в демонстрации: SimplePrinter печатает, но у него физически нет
методов сканирования/факса/копирования (hasattr -> False).
"""

from abc import ABC, abstractmethod


# --------------------------------------------------------------- интерфейсы
# Каждый класс отвечает ровно за одну возможность устройства.
class Printable(ABC):
    """Устройство умеет печатать."""

    @abstractmethod
    def print_document(self, document):
        raise NotImplementedError


class Scannable(ABC):
    """Устройство умеет сканировать."""

    @abstractmethod
    def scan_document(self):
        raise NotImplementedError


class Faxable(ABC):
    """Устройство умеет отправлять факсы."""

    @abstractmethod
    def fax_document(self, document):
        raise NotImplementedError


class Copyable(ABC):
    """Устройство умеет копировать."""

    @abstractmethod
    def copy_document(self):
        raise NotImplementedError


# --------------------------------------------------------------- устройства
class SimplePrinter(Printable):
    """Простой принтер: реализует ТОЛЬКО Printable.

    Нет ни одного метода-заглушки — класс не обязан притворяться,
    что умеет сканировать или отправлять факсы.
    """

    def __init__(self, model="HP LaserJet 1018"):
        self.model = model

    def print_document(self, document):
        print(f"[{self.model}] печать: {document}")


class OfficePrinter(Printable, Scannable, Copyable):
    """Офисный МФУ без факса: печать + сканирование + копирование."""

    def __init__(self, model="Canon i-SENSYS"):
        self.model = model

    def print_document(self, document):
        print(f"[{self.model}] печать: {document}")

    def scan_document(self):
        result = "скан_документа.pdf"
        print(f"[{self.model}] сканирование -> {result}")
        return result

    def copy_document(self):
        print(f"[{self.model}] копирование документа")


class AllInOnePrinter(Printable, Scannable, Faxable, Copyable):
    """Полноценное МФУ: все четыре возможности."""

    def __init__(self, model="Xerox WorkCentre"):
        self.model = model

    def print_document(self, document):
        print(f"[{self.model}] печать: {document}")

    def scan_document(self):
        result = "скан_документа.pdf"
        print(f"[{self.model}] сканирование -> {result}")
        return result

    def fax_document(self, document):
        print(f"[{self.model}] факс: {document}")

    def copy_document(self):
        print(f"[{self.model}] копирование документа")


# ------------------------------------------------- клиентский код (по интерфейсам)
# Функции зависят от узких интерфейсов, а не от «универсального» устройства.
# Поэтому им можно передать любое подходящее устройство.
def print_anything(device: Printable, document):
    """Печатает любой объект, поддерживающий Printable."""
    if not isinstance(device, Printable):
        raise TypeError("Устройство не поддерживает печать")
    device.print_document(document)


def scan_anything(device: Scannable):
    """Сканирует любое устройство, поддерживающее Scannable."""
    if not isinstance(device, Scannable):
        raise TypeError("Устройство не поддерживает сканирование")
    return device.scan_document()


def demo():
    """Демонстрация работы решения по задаче 4."""
    print("=" * 60)
    print("Задача 4. ISP: узкие интерфейсы вместо одного общего")
    print("=" * 60)

    printer = SimplePrinter()
    office = OfficePrinter()
    all_in_one = AllInOnePrinter()

    print("\nПечать (интерфейс Printable):")
    for device in (printer, office, all_in_one):
        print_anything(device, "Домашнее задание.pdf")

    print("\nСканирование (интерфейс Scannable):")
    for device in (office, all_in_one):
        scan_anything(device)

    print("\nФакс (интерфейс Faxable):")
    all_in_one.fax_document("Договор.pdf")

    print("\nЧто умеет каждое устройство:")
    capabilities = [
        ("Printable", Printable),
        ("Scannable", Scannable),
        ("Faxable", Faxable),
        ("Copyable", Copyable),
    ]
    for device in (printer, office, all_in_one):
        supported = [
            name for name, iface in capabilities if isinstance(device, iface)
        ]
        print(f"  {type(device).__name__:<16} -> {', '.join(supported)}")

    # Главное доказательство: у простого принтера нет методов, которых он не умеет.
    print("\nПроверка SimplePrinter:")
    print(f"  есть print_document: {hasattr(printer, 'print_document')}")
    print(f"  есть scan_document:  {hasattr(printer, 'scan_document')}")
    print(f"  есть fax_document:   {hasattr(printer, 'fax_document')}")
    print(f"  есть copy_document:  {hasattr(printer, 'copy_document')}")
    print("  Заглушек с NotImplementedError в классе нет.")

    # Попытка отправить на сканирование принтер без сканера — понятная ошибка.
    try:
        scan_anything(printer)
    except TypeError as error:
        print(f"\nОжидаемая ошибка: {error}")


if __name__ == "__main__":
    demo()
