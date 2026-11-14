"""Текстовое описание графа на языке PlantUML (этап 5)."""

PLANTUML_BEGIN = "@startuml"
PLANTUML_END = "@enduml"
ARROW = " --> "


def edge_lines(graph):
    """Построить строки рёбер графа в виде ``A --> B``."""
    lines = []
    for node in sorted(graph):
        for dep in graph[node]:
            lines.append(node + ARROW + dep)
    return lines


def describe(graph):
    """Сформировать PlantUML-описание графа целиком."""
    lines = [PLANTUML_BEGIN]
    lines.extend(edge_lines(graph))
    lines.append(PLANTUML_END)
    return "\n".join(lines)
