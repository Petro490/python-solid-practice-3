"""
Задача 5. Принцип инверсии зависимостей (DIP).

Что было не так в исходном коде:
    NotificationService сам создавал EmailSender и SMSSender внутри __init__
    и перебирал каналы через if/elif. Высокоуровневый модуль (сервис
    уведомлений) напрямую зависел от низкоуровневых деталей (конкретных
    отправителей). Из-за этого:
      * нельзя было подменить отправителя в тестах (например, на «заглушку»);
      * новый канал (push, telegram) требовал правки сервиса;
      * сервис нельзя было переиспользовать с другим набором каналов.

Что сделано:
    * Notifier — абстракция с методом notify();
    * EmailNotifier, SMSNotifier — реализации этой абстракции;
    * NotificationService принимает Notifier в конструкторе (внедрение
      зависимости), поэтому знает только про интерфейс;
    * PushNotifier добавлен как проверка: новый канал без правки сервиса.

Важный момент: сервис не знает даже, какой контакт нужен каналу (email,
телефон, имя). Это низкоуровневая деталь, поэтому её знает сам notifier:
он принимает пользователя и сам достаёт нужное поле.
"""

from abc import ABC, abstractmethod


# ------------------------------------------------------------------ абстракция
class Notifier(ABC):
    """Абстракция канала уведомлений.

    И высокоуровневый NotificationService, и низкоуровневые отправители
    зависят от этого интерфейса — это и есть инверсия зависимостей.
    """

    @abstractmethod
    def notify(self, user, message):
        """Отправить сообщение пользователю через конкретный канал."""
        raise NotImplementedError

    @property
    def channel_name(self):
        """Человекочитаемое имя канала (для логов и демонстрации)."""
        return type(self).__name__


# --------------------------------------------------------------- реализации
class EmailNotifier(Notifier):
    """Отправка по email. Знает только про email, не про сервис."""

    def notify(self, user, message):
        # Проверка контакта — забота канала, а не сервиса.
        if not user.email:
            raise ValueError(f"У пользователя {user.name} нет email")
        # В реальном коде здесь был бы SMTP-клиент; для демо — вывод в консоль.
        print(f"[EMAIL -> {user.email}] {message}")


class SMSNotifier(Notifier):
    """Отправка по SMS."""

    def notify(self, user, message):
        if not user.phone:
            raise ValueError(f"У пользователя {user.name} нет телефона")
        print(f"[SMS -> {user.phone}] {message}")


class PushNotifier(Notifier):
    """НОВЫЙ канал. Добавлен без изменения NotificationService (проверка DIP)."""

    def notify(self, user, message):
        print(f"[PUSH -> {user.name}] {message}")


class ConsoleNotifier(Notifier):
    """Заглушка для тестов: ничего не отправляет, но запоминает вызовы.

    Такие подмены — главный практический плюс DIP.
    """

    def __init__(self):
        self.sent = []

    def notify(self, user, message):
        self.sent.append((user.name, message))


# ------------------------------------------------------- высокоуровневый модуль
class User:
    """Простой пользователь с контактами для разных каналов."""

    def __init__(self, name, email, phone=None):
        self.name = name
        self.email = email
        self.phone = phone


class NotificationService:
    """Сервис уведомлений, зависящий от абстракции Notifier.

    Сервис НЕ создаёт отправителей и НЕ знает, email это, SMS или push.
    Достаточно передать нужную реализацию в конструктор.
    """

    def __init__(self, notifier: Notifier):
        # Проверяем контракт на входе: сервис принимает только Notifier.
        if not isinstance(notifier, Notifier):
            raise TypeError("Ожидался объект, реализующий Notifier")
        self.notifier = notifier

    def notify_user(self, user, message):
        """Отправить уведомление пользователю через внедрённый канал."""
        # Сервис отвечает только за сценарий «уведомить пользователя».
        # Как именно отправлять и какой контакт брать — решает notifier.
        self.notifier.notify(user, message)


class MultiNotifier(Notifier):
    """Композитный канал: отправляет сразу в несколько каналов.

    Ещё одно расширение без правки NotificationService: для сервиса это
    по-прежнему просто Notifier.
    """

    def __init__(self, *notifiers):
        self._notifiers = list(notifiers)

    def notify(self, user, message):
        for notifier in self._notifiers:
            notifier.notify(user, message)


def demo():
    """Демонстрация работы решения по задаче 5."""
    print("=" * 60)
    print("Задача 5. DIP: NotificationService зависит от Notifier")
    print("=" * 60)

    user = User("Анна", email="anna@example.com", phone="+7 900 123-45-67")

    # Один и тот же сервис работает с любым каналом — зависимость внедряется.
    print("\nEmail-канал:")
    NotificationService(EmailNotifier()).notify_user(user, "Заказ собран")

    print("\nSMS-канал:")
    NotificationService(SMSNotifier()).notify_user(user, "Курьер в пути")

    print("\nНовый push-канал (сервис не менялся):")
    NotificationService(PushNotifier()).notify_user(user, "Скидка 20% на всё")

    print("\nТестовая заглушка вместо реальной отправки:")
    fake = ConsoleNotifier()
    NotificationService(fake).notify_user(user, "Тестовое сообщение")
    print(f"  заглушка зафиксировала вызовов: {len(fake.sent)} -> {fake.sent}")

    print("\nКомпозитный канал (email + SMS одновременно):")
    NotificationService(MultiNotifier(EmailNotifier(), SMSNotifier())).notify_user(
        user, "Важное объявление"
    )


if __name__ == "__main__":
    demo()
