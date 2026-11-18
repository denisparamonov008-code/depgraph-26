"""Разбор и проверка параметров командной строки (этап 1)."""

import argparse
import os

from depgraph.graph import dfs_iterative, load_test_repo
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
    parser.add_argument("--load-order", default="off",
                        help="показать порядок загрузки (on/off)")
    parser.add_argument("--plantuml", default="off",
                        help="показать граф на языке PlantUML (on/off)")
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
        "load_order": parse_flag(args.load_order),
        "plantuml": parse_flag(args.plantuml),
    }


def format_params(settings):
    """Отформатировать настройки строками ключ-значение."""
    lines = []
    keys = ("package", "repo", "test_mode", "filter",
            "load_order", "plantuml")
    for key in keys:
        lines.append("%s=%s" % (key, settings[key]))
    return "\n".join(lines)


def make_skip(needle):
    """Построить проверку подстроки фильтра для имён пакетов."""
    def skip(name):
        return needle in name
    return skip


def print_test_graph(settings):
    """Построить и вывести граф из тестового файла (этапы 3-5)."""
    from depgraph.order import load_order
    from depgraph.plantuml import describe
    graph = load_test_repo(settings["repo"])
    needle = settings["filter"]
    if needle:
        skip = make_skip(needle)
    else:
        skip = None
    order, cycles = dfs_iterative(settings["package"],
                                  graph.get, skip)
    print("graph order:")
    for name in order:
        print("  " + name)
    if cycles:
        print("cycles:")
        for found in cycles:
            print("  " + " -> ".join(found))
    if settings["load_order"]:
        print("load order:")
        for name in load_order(settings["package"], graph.get,
                               skip):
            print("  " + name)
    if settings["plantuml"]:
        print("plantuml:")
        print(describe(graph))
    return 0


def main(argv=None):
    """Точка входа: параметры, затем зависимости (этапы 2-3)."""
    try:
        settings = validate(parse_args(argv))
    except ConfigError as err:
        print("ошибка: %s" % err)
        return 2
    print(format_params(settings))
    if settings["test_mode"] and os.path.isfile(settings["repo"]):
        return print_test_graph(settings)
    try:
        deps = direct_dependencies(settings["package"],
                                   settings["repo"])
    except Exception as err:
        print("ошибка: %s" % err)
        return 1
    print("dependencies:")
    for name in deps:
        print("  " + name)
    return 0
