"""Тести для lab7.py."""
import contextlib
import io
import os
import tempfile
import unittest
from unittest.mock import patch

import lab7

BOOKS = [
    ("Шевченко", "Кобзар", 1840),
    ("Франко", "Захар Беркут", 1883),
    ("Українка", "Лісова пісня", 1911),
    ("Шевченко", "Катерина", 1840),
]
CONTENT = (
    "Шевченко,Кобзар,1840\n"
    "Франко,Захар Беркут,1883\n"
    "Українка,Лісова пісня,1911\n"
    "Шевченко,Катерина,1840\n"
)


class TestFunctions(unittest.TestCase):
    def test_parse_book(self):
        self.assertEqual(lab7.parse_book("Шевченко,Кобзар,1840\n"), ("Шевченко", "Кобзар", 1840))
        self.assertEqual(lab7.parse_book(" Франко , Захар Беркут , 1883 "), ("Франко", "Захар Беркут", 1883))

    def test_parse_book_errors(self):
        for bad in ("Шевченко,Кобзар", "Шевченко,Кобзар,abc", ",Кобзар,1840", "a,b,c,1840"):
            with self.subTest(line=bad):
                with self.assertRaises(ValueError):
                    lab7.parse_book(bad)

    def test_format_book(self):
        self.assertEqual(lab7.format_book(BOOKS[0]), "Кобзар (Шевченко, 1840)")

    def test_book_to_line(self):
        self.assertEqual(lab7.book_to_line(BOOKS[1]), "Франко,Захар Беркут,1883")

    def test_filter_by_year(self):
        self.assertEqual(lab7.filter_by_year(BOOKS, 1840), [BOOKS[0], BOOKS[3]])
        self.assertEqual(lab7.filter_by_year(BOOKS, 2000), [])

    def test_remove_author(self):
        self.assertEqual(lab7.remove_author(BOOKS, "Шевченко"), [BOOKS[1], BOOKS[2]])
        self.assertEqual(lab7.remove_author(BOOKS, "шевченко"), [BOOKS[1], BOOKS[2]])
        self.assertEqual(lab7.remove_author(BOOKS, "Невідомий"), BOOKS)

    def test_sort_books_by_year(self):
        years = [b[2] for b in lab7.sort_books_by_year(BOOKS)]
        self.assertEqual(years, [1840, 1840, 1883, 1911])
        years = [b[2] for b in lab7.sort_books_by_year(BOOKS, reverse=True)]
        self.assertEqual(years, [1911, 1883, 1840, 1840])


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.old_cwd = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def write(self, name, text):
        with open(name, "w", encoding="utf-8") as file:
            file.write(text)

    def read(self, name):
        with open(name, encoding="utf-8") as file:
            return file.read()

    def test_read_books(self):
        self.write("b.txt", CONTENT)
        books, errors = lab7.read_books("b.txt")
        self.assertEqual(books, BOOKS)
        self.assertEqual(errors, [])

    def test_read_books_skips_bad_and_empty_lines(self):
        self.write("b.txt", "Шевченко,Кобзар,1840\n\nпомилка\nФранко,Захар Беркут,1883\n")
        books, errors = lab7.read_books("b.txt")
        self.assertEqual(len(books), 2)
        self.assertEqual(len(errors), 1)
        self.assertIn("рядок 3", errors[0])

    def test_read_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            lab7.read_books("missing.txt")

    def test_write_and_read_roundtrip(self):
        lab7.write_books("out.txt", BOOKS)
        self.assertEqual(self.read("out.txt"), CONTENT)
        self.assertEqual(lab7.read_books("out.txt")[0], BOOKS)

    def run_main(self, answers):
        output = io.StringIO()
        with patch("builtins.input", side_effect=answers), contextlib.redirect_stdout(output):
            code = lab7.main()
        return code, output.getvalue()

    def test_main_full_flow(self):
        self.write("books.txt", CONTENT)
        code, out = self.run_main(["1840", "books.txt", "", "н"])
        self.assertEqual(code, 0)
        self.assertIn("Кобзар (Шевченко, 1840)", out)
        self.assertEqual(self.read("books_by_year.txt"),
                         "Шевченко,Кобзар,1840\nШевченко,Катерина,1840\n")
        self.assertIn("Видалено книг автора «Шевченко»: 2", out)
        self.assertEqual(self.read("books.txt"), CONTENT)  # без згоди файл не змінюється

    def test_main_saves_changes_when_confirmed(self):
        self.write("books.txt", CONTENT)
        code, out = self.run_main(["1883", "books.txt", "Франко", "т"])
        self.assertEqual(code, 0)
        self.assertNotIn("Франко", self.read("books.txt"))

    def test_main_invalid_year_is_asked_again(self):
        self.write("books.txt", CONTENT)
        code, out = self.run_main(["abc", "18400", "1883", "books.txt", "", "н"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("Помилка: рік має бути цілим числом"), 2)
        self.assertEqual(self.read("books_by_year.txt"), "Франко,Захар Беркут,1883\n")

    def test_main_year_without_books(self):
        self.write("books.txt", CONTENT)
        code, out = self.run_main(["2000", "books.txt", "", "н"])
        self.assertIn("не знайдено", out)
        self.assertFalse(os.path.exists("books_by_year.txt"))

    def test_main_missing_books_file(self):
        code, out = self.run_main([])
        self.assertEqual(code, 1)
        self.assertIn("Файл books.txt не знайдено!", out)

    def test_main_missing_user_file(self):
        self.write("books.txt", CONTENT)
        code, out = self.run_main(["1840", "gfddfg", ""])
        self.assertEqual(code, 1)
        self.assertIn("Файл gfddfg не знайдено!", out)

    def test_main_directory_as_filename(self):
        self.write("books.txt", CONTENT)
        os.mkdir("folder")
        code, out = self.run_main(["1840", "folder", ""])
        self.assertEqual(code, 1)
        self.assertIn("Помилка читання файлу folder", out)


if __name__ == "__main__":
    unittest.main()
