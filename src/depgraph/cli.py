"""Разбор и проверка параметров командной строки (этап 1)."""

import argparse

from depgraph.nuget import direct_dependencies

MAX_FILTER_LENGTH = 64


class ConfigError(Exception):
    """Ошибка в параметрах запуска."""


def parse_flag(value):
    """Превратить строку в логическое значение флага."""
    text = value.strip().lower()
    if text in ("1", "true", "on", "yes"):
        return True
    if text in ("0", "false", "off", "no"):
        return False
    raise ConfigError("флаг должен быть on/off, true/false или 1/0")


def build_parser():
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей NuGet")
    parser.add_argument("--package", required=True,
                        help="имя анализируемого пакета")
    parser.add_argument("--repo", required=True,
                        help="URL репозитория или файл тестового репозитория")
    parser.add_argument("--test-mode", default="off",
                        help="режим тестового репозитория (on/off)")
    parser.add_argument("--filter", default="",
                        help="подстрока для фильтрации пакетов")
    return parser


def parse_args(argv=None):
    """Разобрать аргументы и вернуть параметры запуска."""
    return build_parser().parse_args(argv)


def check_package(value):
    """Проверить имя пакета: не должно быть пустым."""
    if not value or not value.strip():
        raise ConfigError("имя пакета не должно быть пустым")
    return value.strip()


def check_repo(value):
    """Проверить адрес репозитория: URL или существующий файл."""
    import os
    text = (value or "").strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    if text and os.path.isfile(text):
        return text
    raise ConfigError("repo должен быть URL или существующим файлом")


def check_filter(value):
    """Проверить подстроку фильтра: не длиннее предела."""
    text = value or ""
    if len(text) > MAX_FILTER_LENGTH:
        raise ConfigError("фильтр длиннее %d символов" % MAX_FILTER_LENGTH)
    return text


def validate(args):
    """Проверить все параметры, вернуть словарь настроек."""
    return {
        "package": check_package(args.package),
        "repo": check_repo(args.repo),
        "test_mode": parse_flag(args.test_mode),
        "filter": check_filter(args.filter),
    }


def format_params(settings):
    """Отформатировать настройки строками ключ-значение."""
    lines = []
    for key in ("package", "repo", "test_mode", "filter"):
        lines.append("%s=%s" % (key, settings[key]))
    return "\n".join(lines)


def main(argv=None):
    """Точка входа: параметры, затем прямые зависимости (этап 2)."""
    try:
        settings = validate(parse_args(argv))
    except ConfigError as err:
        print("ошибка: %s" % err)
        return 2
    print(format_params(settings))
    try:
        deps = direct_dependencies(settings["package"],
                                   settings["repo"])
    except Exception as err:  # сеть недоступна: честно сообщаем
        print("ошибка: %s" % err)
        return 1
    print("dependencies:")
    for name in deps:
        print("  " + name)
    return 0
