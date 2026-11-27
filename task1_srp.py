"""
Задача 1. Принцип единственной ответственности (SRP).

Что было не так в исходном коде:
    класс Journal одновременно умел:
      1) хранить и изменять записи (add_entry, remove_entry, __str__);
      2) работать с файловой системой (save, load);
      3) работать с сетью (load_from_web).
    То есть у класса было три причины для изменения. Если, например, нужно
    поменять формат хранения (JSON вместо txt), приходится править класс,
    который отвечает за бизнес-логику журнала.

Что сделано:
    * Journal — только управление записями (добавление, удаление, поиск);
    * JournalPersistence — только сохранение/загрузка (статические методы,
      потому что состояние хранить не нужно: журнал передаётся параметром).
"""


class Journal:
    """Журнал записей.

    Единственная ответственность: хранить записи и позволять ими управлять.
    Класс ничего не знает о файлах, сети, email и т.п.
    """

    def __init__(self):
        # Записи храним в "приватном" списке: снаружи меняем их только методами.
        self._entries = []
        # Счётчик нужен, чтобы нумерация записей не сбивалась после удаления.
        self._count = 0

    # ------------------------------------------------------------------ чтение
    @property
    def entries(self):
        """Копия списка записей — чтобы внешний код не ломал инкапсуляцию."""
        return list(self._entries)

    @property
    def count(self):
        """Последний выданный номер записи."""
        return self._count

    def __len__(self):
        """len(journal) -> количество записей (удобно и читаемо)."""
        return len(self._entries)

    def __str__(self):
        """Текстовое представление: записи по одной на строку."""
        return "\n".join(self._entries)

    # ---------------------------------------------------------------- изменение
    def add_entry(self, text):
        """Добавить запись и вернуть её номер.

        Номер берётся из счётчика, а не из len(self._entries):
        после удаления записи номера не должны выдаваться повторно.
        """
        self._count += 1
        self._entries.append(f"{self._count}: {text}")
        return self._count

    def remove_entry(self, index):
        """Удалить запись по индексу (отрицательные индексы тоже работают)."""
        del self._entries[index]

    def clear(self):
        """Очистить журнал, но сохранить нумерацию (счётчик не сбрасываем)."""
        self._entries.clear()

    # -------------------------------------------------------------------- поиск
    def find(self, substring):
        """Вернуть записи, содержащие подстроку (поиск без учёта регистра).

        Это тоже «управление записями», поэтому метод живёт в Journal,
        а не в отдельном классе.
        """
        needle = substring.lower()
        return [entry for entry in self._entries if needle in entry.lower()]

    # ------------------------------------------------- восстановление состояния
    def replace_entries(self, entries):
        """Полностью заменить содержимое журнала.

        Нужен для загрузки из внешнего источника (файл, сеть). Сам Journal
        по-прежнему не знает, ОТКУДА пришли строки — он только принимает данные.
        Счётчик восстанавливаем по номерам в строках вида "3: текст".
        """
        self._entries = list(entries)
        self._count = self._detect_last_number(self._entries)

    @staticmethod
    def _detect_last_number(entries):
        """Найти максимальный номер записи, чтобы нумерация продолжилась верно."""
        last = 0
        for entry in entries:
            number, separator, _ = entry.partition(":")
            if separator and number.strip().isdigit():
                last = max(last, int(number))
        # Если номера найти не удалось (файл «чужого» формата) — берём длину.
        return last or len(entries)


class JournalPersistence:
    """Сохранение и загрузка журнала.

    Единственная ответственность: превращать журнал в файл и обратно.
    Методы статические, потому что объекту нечего хранить в состоянии:
    журнал передаётся аргументом. Благодаря этому класс легко тестировать.
    """

    @staticmethod
    def save(journal, filename):
        """Сохранить журнал в текстовый файл (UTF-8, одна запись — одна строка)."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(str(journal))

    @staticmethod
    def load(journal, filename):
        """Загрузить журнал из файла и вернуть его же (удобно для цепочки вызовов)."""
        with open(filename, "r", encoding="utf-8") as file:
            # splitlines() убирает переводы строк и не создаёт пустую запись
            # в конце файла, в отличие от readlines() в исходном коде.
            lines = file.read().splitlines()
        journal.replace_entries(lines)
        return journal

    @staticmethod
    def load_from_web(journal, uri):
        """Загрузить журнал по HTTP(S).

        Логика сети — тоже ответственность «доставки данных», поэтому метод
        остался здесь, а не в Journal. В демонстрации не вызывается:
        без интернета он закончится ошибкой, и это нормально для учебного примера.
        """
        import urllib.request

        with urllib.request.urlopen(uri, timeout=10) as response:
            text = response.read().decode("utf-8")
        journal.replace_entries(text.splitlines())
        return journal


class JournalEmailSender:
    """Пример расширения функциональности БЕЗ правки Journal и JournalPersistence.

    Появилась новая обязанность (отправка по email) — появился новый класс.
    Ни один существующий класс менять не пришлось: это и есть польза от SRP.
    Здесь отправка имитируется выводом в консоль, чтобы пример работал офлайн.
    """

    @staticmethod
    def send(journal, address):
        """«Отправить» журнал на адрес и вернуть количество записей."""
        print(f"[email -> {address}] отправлено записей: {len(journal)}")
        print(str(journal))
        return len(journal)


def demo():
    """Демонстрация работы решения по задаче 1."""
    from pathlib import Path

    print("=" * 60)
    print("Задача 1. SRP: Journal + JournalPersistence")
    print("=" * 60)

    journal = Journal()
    journal.add_entry("Купить молоко")
    journal.add_entry("Позвонить в сервис")
    journal.add_entry("Сдать практическую работу")

    # Поиск — часть управления записями.
    print("\nПоиск по слову 'сдать':")
    for entry in journal.find("сдать"):
        print("  ", entry)

    journal.remove_entry(1)
    print("\nПосле удаления второй записи:")
    print(journal)

    # Сохранение и загрузка вынесены в отдельный класс.
    path = Path(__file__).with_name("journal_demo.txt")
    JournalPersistence.save(journal, path)
    print(f"\nЖурнал сохранён в файл: {path.name}")

    restored = JournalPersistence.load(Journal(), path)
    print("Журнал загружен обратно:")
    print(restored)

    # Проверяем, что нумерация продолжилась, а не началась с нуля.
    new_number = restored.add_entry("Проверить нумерацию после загрузки")
    print(f"\nНовая запись получила номер {new_number} (счётчик восстановлен)")

    # Новая функциональность — новый класс, старые не тронуты.
    JournalEmailSender.send(restored, "teacher@example.com")

    path.unlink(missing_ok=True)  # убираем временный файл после демонстрации


if __name__ == "__main__":
    demo()
