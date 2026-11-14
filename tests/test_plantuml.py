"""Тесты PlantUML-описания графа (этап 5)."""

import os
import unittest

from depgraph.graph import load_test_repo
from depgraph.plantuml import describe

HERE = os.path.dirname(os.path.abspath(__file__))


def data(name):
    """Путь к файлу тестового репозитория."""
    return os.path.join(HERE, "testdata", name)


class TestPlantuml(unittest.TestCase):
    """Проверка формирования диаграммы."""

    def test_frame(self):
        """Описание обёрнуто в @startuml/@enduml."""
        graph = load_test_repo(data("chain.txt"))
        text = describe(graph)
        lines = text.splitlines()
        self.assertEqual(lines[0], "@startuml")
        self.assertEqual(lines[-1], "@enduml")

    def test_edges(self):
        """Все рёбра присутствуют в виде стрелок."""
        graph = load_test_repo(data("branch.txt"))
        text = describe(graph)
        self.assertIn("A --> B", text)
        self.assertIn("A --> C", text)
        self.assertIn("B --> D", text)
        self.assertIn("C --> D", text)

    def test_cycle(self):
        """Цикл описывается тремя стрелками."""
        graph = load_test_repo(data("cycle.txt"))
        text = describe(graph)
        self.assertIn("C --> A", text)


if __name__ == "__main__":
    unittest.main()
