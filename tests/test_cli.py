"""Тесты прототипа CLI (этап 1)."""

import unittest

from depgraph.cli import (
    ConfigError,
    check_filter,
    check_package,
    check_repo,
    format_params,
    main,
    parse_args,
    parse_flag,
    validate,
)


class TestParseArgs(unittest.TestCase):
    """Проверка разбора аргументов."""

    def test_defaults(self):
        """Значения по умолчанию для флага и фильтра."""
        args = parse_args(["--package", "A", "--repo", "https://x/y"])
        self.assertEqual(args.test_mode, "off")
        self.assertEqual(args.filter, "")

    def test_missing_value_exits(self):
        """Отсутствие значения завершает работу с кодом 2."""
        with self.assertRaises(SystemExit) as ctx:
            parse_args(["--package"])
        self.assertEqual(ctx.exception.code, 2)

    def test_flag_values(self):
        """Флаг понимает on/off, true/false, 1/0."""
        for good in ("on", "true", "1", "yes", "OFF", "False", "0", "no"):
            self.assertIn(parse_flag(good), (True, False))

    def test_flag_bad_value(self):
        """Мусор во флаге даёт ошибку настроек."""
        with self.assertRaises(ConfigError):
            parse_flag("maybe")


class TestValidate(unittest.TestCase):
    """Проверка настроек целиком."""

    def test_empty_package(self):
        """Пустое имя пакета запрещено."""
        with self.assertRaises(ConfigError):
            check_package("   ")

    def test_repo_must_exist(self):
        """Несуществующий путь отклоняется."""
        with self.assertRaises(ConfigError):
            check_repo("/нет/такого/файла.txt")

    def test_filter_too_long(self):
        """Слишком длинный фильтр отклоняется."""
        with self.assertRaises(ConfigError):
            check_filter("x" * 65)

    def test_format(self):
        """Вывод настроек идёт строками ключ-значение."""
        args = parse_args(["--package", "A",
                           "--repo", "https://x/y",
                           "--test-mode", "on",
                           "--filter", "test"])
        text = format_params(validate(args))
        self.assertIn("package=A", text)
        self.assertIn("test_mode=True", text)

    def test_main_bad_flag(self):
        """Программа возвращает 2 при плохом флаге."""
        code = main(["--package", "A", "--repo", "https://x/y",
                     "--test-mode", "maybe"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
