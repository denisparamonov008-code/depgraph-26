"""Тесты построения графа (этап 3)."""

import os
import unittest

from depgraph.graph import dfs_iterative, load_test_repo

HERE = os.path.dirname(os.path.abspath(__file__))


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(HERE, "testdata", name)


def getter(graph):
    """Получить зависимости вершины из словаря."""
    return lambda node: graph.get(node, [])


def make_skip(letter):
    """Построить проверку: пропускать имена с заданной буквой."""
    def skip(name):
        return letter in name
    return skip


class TestGraph(unittest.TestCase):
    """Проверка загрузки файла и обхода в глубину."""

    def test_load(self):
        """Файл читается в словарь смежности."""
        graph = load_test_repo(data("chain.txt"))
        self.assertEqual(graph, {"A": ["B"], "B": ["C"], "C": []})

    def test_chain_order(self):
        """Линейная цепочка обходится по порядку."""
        graph = load_test_repo(data("chain.txt"))
        order, cycles = dfs_iterative("A", getter(graph))
        self.assertEqual(order, ["A", "B", "C"])
        self.assertEqual(cycles, [])

    def test_branch(self):
        """Ветвление обходится без повторов."""
        graph = load_test_repo(data("branch.txt"))
        order, cycles = dfs_iterative("A", getter(graph))
        self.assertEqual(order[0], "A")
        self.assertEqual(sorted(order), ["A", "B", "C", "D"])
        self.assertEqual(cycles, [])

    def test_cycle(self):
        """Цикл находится и обход завершается."""
        graph = load_test_repo(data("cycle.txt"))
        order, cycles = dfs_iterative("A", getter(graph))
        self.assertEqual(sorted(order), ["A", "B", "C"])
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0][0], cycles[0][-1])

    def test_filter(self):
        """Пакеты с подстрокой пропускаются."""
        graph = load_test_repo(data("branch.txt"))
        order, _ = dfs_iterative("A", getter(graph),
                                 make_skip("B"))
        self.assertNotIn("B", order)
        self.assertIn("C", order)

    def test_skip_start(self):
        """Отфильтрованный старт даёт пустой обход."""
        graph = load_test_repo(data("chain.txt"))
        order, cycles = dfs_iterative("A", getter(graph),
                                      make_skip("A"))
        self.assertEqual(order, [])
        self.assertEqual(cycles, [])


if __name__ == "__main__":
    unittest.main()
