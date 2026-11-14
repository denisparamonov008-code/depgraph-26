"""Тесты получения зависимостей NuGet (этап 2)."""

import json
import os
import unittest

from depgraph.nuget import (
    direct_dependencies,
    leaf_dependencies,
    leaf_url,
    list_versions,
)

HERE = os.path.dirname(os.path.abspath(__file__))


def load_fixture(name):
    """Прочитать JSON-приспособление из папки tests/fixtures."""
    path = os.path.join(HERE, "fixtures", name)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fake_opener(mapping):
    """Подменить сеть словарём адрес-ответ."""
    def opener(url):
        return mapping.get(url, {"items": []})
    return opener


class TestNuget(unittest.TestCase):
    """Проверка разбора ответов регистрации NuGet."""

    def test_versions(self):
        """Из регистрации извлекаются все версии."""
        reg = load_fixture("registration.json")
        self.assertEqual(list_versions(reg), ["1.0.0", "2.0.0"])

    def test_leaf_url(self):
        """Для версии находится адрес её карточки."""
        reg = load_fixture("registration.json")
        url = leaf_url(reg, "2.0.0")
        self.assertIsNotNone(url)
        self.assertTrue(url.endswith("2.0.0.json"))

    def test_leaf_deps(self):
        """Из карточки извлекаются имена зависимостей."""
        leaf = load_fixture("leaf.json")
        self.assertEqual(leaf_dependencies(leaf), ["DepA", "DepB"])

    def test_direct(self):
        """Сквозной разбор: регистрация плюс карточка."""
        reg = load_fixture("registration.json")
        leaf = load_fixture("leaf.json")
        mapping = {
            "https://repo.example/x/demo/index.json": reg,
            "https://repo.example/x/demo/2.0.0.json": leaf,
        }
        deps = direct_dependencies("Demo", "https://repo.example/x",
                                   fake_opener(mapping))
        self.assertEqual(deps, ["DepA", "DepB"])

    def test_empty(self):
        """Пустая регистрация даёт пустой список."""
        deps = direct_dependencies("Demo", "https://repo.example/x",
                                   fake_opener({}))
        self.assertEqual(deps, [])


if __name__ == "__main__":
    unittest.main()
