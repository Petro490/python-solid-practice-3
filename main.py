"""
Практическая работа №3: ООП в Python. SOLID на практике.

Запуск всей работы:      python main.py
Запуск одной задачи:     python main.py 3
Запуск файла отдельно:   python task3_lsp.py
"""

import sys

import task1_srp
import task2_ocp
import task3_lsp
import task4_isp
import task5_dip

# Список задач в порядке практической работы: (номер, заголовок, функция демо).
TASKS = [
    (1, "SRP — единственная ответственность", task1_srp.demo),
    (2, "OCP — открытость/закрытость", task2_ocp.demo),
    (3, "LSP — подстановка Лисков", task3_lsp.demo),
    (4, "ISP — разделение интерфейса", task4_isp.demo),
    (5, "DIP — инверсия зависимостей", task5_dip.demo),
]


def main():
    """Запустить все задачи или одну, номер которой передан аргументом."""
    selected = set()

    # Разбор аргумента командной строки: main.py 2 4 — только эти задачи.
    for argument in sys.argv[1:]:
        if not argument.isdigit() or not 1 <= int(argument) <= len(TASKS):
            print(f"Неизвестный номер задачи: {argument}")
            print("Допустимо: 1..5, например: python main.py 3")
            return 1
        selected.add(int(argument))

    for number, title, demo in TASKS:
        if selected and number not in selected:
            continue
        demo()
        print()  # пустая строка между задачами для читаемого вывода

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
