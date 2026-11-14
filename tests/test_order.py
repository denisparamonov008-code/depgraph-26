"""Тесты порядка загрузки (этап 4)."""

import os
import unittest

from depgraph.graph import load_test_repo
from depgraph.order import load_order

HERE = os.path.dirname(os.path.abspath(__file__))


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(HERE, "testdata", name)


def getter(graph):
    """Получить зависимости вершины из словаря."""
    return lambda node: graph.get(node, [])


class TestOrder(unittest.TestCase):
    """Проверка топологического порядка загрузки."""

    def test_chain(self):
        """Цепочка грузится с конца: C, B, A."""
        graph = load_test_repo(data("chain.txt"))
        self.assertEqual(load_order("A", getter(graph)),
                         ["C", "B", "A"])

    def test_branch(self):
        """Общая зависимость первая, стартовая последняя."""
        graph = load_test_repo(data("branch.txt"))
        order = load_order("A", getter(graph))
        self.assertEqual(order[0], "D")
        self.assertEqual(order[-1], "A")
        self.assertEqual(sorted(order), ["A", "B", "C", "D"])

    def test_cycle_finishes(self):
        """Цикл не вешает программу, все вершины в порядке."""
        graph = load_test_repo(data("cycle.txt"))
        order = load_order("A", getter(graph))
        self.assertEqual(sorted(order), ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
