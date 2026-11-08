"""Лабораторна робота №7. Читання та запис даних у файли (варіант 5).

Програма працює з файлом ``books.txt``, де кожен рядок має формат
``Автор,Назва,Рік``:

1. читає всі записи та виводить їх у форматі «Назва (Автор, Рік)»;
2. запитує рік видання та записує книги цього року у ``books_by_year.txt``;
3. запитує ім'я файлу, видаляє з нього всі книги вказаного автора
   (за замовчуванням «Шевченко») та виводить оновлений список.
"""
import sys

BOOKS_FILE = "books.txt"
BY_YEAR_FILE = "books_by_year.txt"
DEFAULT_AUTHOR = "Шевченко"


# ---------------------------------------------------------------------------
# Робота з записами
# ---------------------------------------------------------------------------
def parse_book(line):
    """Розбирає рядок формату «Автор,Назва,Рік».

    Args:
        line: Рядок з файлу.

    Returns:
        Кортеж ``(автор, назва, рік)``, де рік - ціле число.

    Raises:
        ValueError: якщо рядок має некоректний формат.
    """
    parts = [part.strip() for part in line.strip().split(",")]
    if len(parts) != 3 or not all(parts):
        raise ValueError(f"очікується формат «Автор,Назва,Рік», отримано «{line.strip()}»")
    author, title, year = parts
    if not (year.isascii() and year.isdigit()):
        raise ValueError(f"рік має бути числом, отримано «{year}»")
    return author, title, int(year)


def book_to_line(book):
    """Перетворює кортеж ``(автор, назва, рік)`` на рядок «Автор,Назва,Рік»."""
    author, title, year = book
    return f"{author},{title},{year}"


def format_book(book):
    """Форматує книгу у вигляді «Назва (Автор, Рік)»."""
    author, title, year = book
    return f"{title} ({author}, {year})"


def read_books(filename):
    """Читає книги з файлу.

    Порожні рядки пропускаються. Некоректні рядки не зупиняють
    читання: вони пропускаються, а їх опис додається до списку помилок.

    Args:
        filename: Ім'я текстового файлу (UTF-8).

    Returns:
        Кортеж ``(books, errors)``: список книг та список повідомлень
        про пропущені рядки.

    Raises:
        FileNotFoundError: якщо файл не знайдено.
        OSError: при інших помилках введення-виведення.
    """
    books, errors = [], []
    with open(filename, "r", encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                books.append(parse_book(line))
            except ValueError as error:
                errors.append(f"рядок {number}: {error}")
    return books, errors


def write_books(filename, books):
    """Записує книги у файл у форматі «Автор,Назва,Рік» (по одній на рядок).

    Raises:
        OSError: якщо файл неможливо записати.
    """
    with open(filename, "w", encoding="utf-8") as file:
        for book in books:
            file.write(book_to_line(book) + "\n")


def filter_by_year(books, year):
    """Повертає книги, видані у вказаному році."""
    return [book for book in books if book[2] == year]


def remove_author(books, author):
    """Повертає книги без творів вказаного автора (регістр не враховується)."""
    wanted = author.casefold()
    return [book for book in books if book[0].casefold() != wanted]


def sort_books_by_year(books, reverse=False):
    """Сортує книги за роком видання (за зростанням, або за спаданням при ``reverse=True``)."""
    return sorted(books, key=lambda book: book[2], reverse=reverse)


# ---------------------------------------------------------------------------
# Взаємодія з користувачем
# ---------------------------------------------------------------------------
def print_books(books):
    """Виводить книги на екран у форматі «Назва (Автор, Рік)»."""
    if not books:
        print("(список порожній)")
    for book in books:
        print(format_book(book))


def ask_year():
    """Запитує рік видання, доки користувач не введе коректне значення."""
    while True:
        text = input("Введіть рік видання: ").strip()
        if text.isascii() and text.isdigit() and len(text) <= 4:
            return int(text)
        print("Помилка: рік має бути цілим числом (наприклад, 1883).")


def main():
    # 1-3. Відкриття та читання books.txt, виведення записів
    try:
        books, errors = read_books(BOOKS_FILE)
    except FileNotFoundError:
        print(f"Файл {BOOKS_FILE} не знайдено!")
        return 1
    except UnicodeDecodeError:
        print(f"Файл {BOOKS_FILE} має бути в кодуванні UTF-8!")
        return 1
    except IOError:
        print(f"Помилка читання файлу {BOOKS_FILE}")
        return 1

    for message in errors:
        print(f"Пропущено {message}")
    print(f"Вміст файлу {BOOKS_FILE}:")
    print_books(books)
    print()

    # 4-5. Запит року та запис книг цього року у books_by_year.txt
    year = ask_year()
    selected = filter_by_year(books, year)
    if selected:
        try:
            write_books(BY_YEAR_FILE, selected)
            print(f"Книги {year} року ({len(selected)} шт.) записано у файл {BY_YEAR_FILE}")
        except IOError:
            print(f"Помилка запису у файл {BY_YEAR_FILE}")
    else:
        print(f"Книг, виданих у {year} році, не знайдено. Файл {BY_YEAR_FILE} не створено.")
    print()

    # 6-7. Запит імені файлу, видалення книг автора, виведення результату
    filename = input("Введіть ім'я файлу, з якого потрібно видалити книги автора: ").strip()
    author = input(f"Введіть прізвище автора (Enter - {DEFAULT_AUTHOR}): ").strip() or DEFAULT_AUTHOR
    try:
        file_books, file_errors = read_books(filename)
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено!")
        return 1
    except UnicodeDecodeError:
        print(f"Файл {filename} має бути в кодуванні UTF-8!")
        return 1
    except IOError:
        print(f"Помилка читання файлу {filename}")
        return 1

    updated = remove_author(file_books, author)
    removed = len(file_books) - len(updated)
    print(f"Видалено книг автора «{author}»: {removed}")
    print("Оновлений список книг:")
    print_books(updated)

    if removed:
        answer = input(f"Записати зміни у файл {filename}? (т/н): ").strip().lower()
        if answer in ("т", "y", "так", "yes"):
            try:
                write_books(filename, updated)
                print(f"Зміни записано у файл {filename}")
            except IOError:
                print(f"Помилка запису у файл {filename}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EOFError, KeyboardInterrupt):
        print("\nРоботу перервано користувачем.")
        sys.exit(1)
