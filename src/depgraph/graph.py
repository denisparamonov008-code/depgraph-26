"""Построение графа зависимостей (этап 3).

Тестовый репозиторий — текстовый файл, каждая строка вида
``ПАКЕТ: ЗАВИСИМОСТЬ1 ЗАВИСИМОСТЬ2``. Пустые строки и строки,
начинающиеся с `#`, пропускаются. Имена пакетов — большие
латинские буквы.
"""

COMMENT_PREFIX = "#"
SEPARATOR = ":"


def load_test_repo(path):
    """Прочитать тестовый репозиторий в словарь пакет-список."""
    graph = {}
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith(COMMENT_PREFIX):
                continue
            if SEPARATOR not in line:
                continue
            head, _, tail = line.partition(SEPARATOR)
            graph[head.strip()] = tail.split()
    return graph


def _enter(node, iters, get_deps, path, path_set, order):
    """Войти в вершину: запустить итератор и положить в путь."""
    iters[node] = iter(get_deps(node) or [])
    path.append(node)
    path_set.add(node)
    order.append(node)


def _leave(node, stack, finished, path, path_set):
    """Покинуть вершину: снять со стека и отметить готовой."""
    stack.pop()
    finished.add(node)
    if path and path[-1] == node:
        path.pop()
        path_set.discard(node)


def _take_child(node_iter, finished, path, path_set, skip, cycles):
    """Взять следующего потомка; обратные рёбра записать в циклы."""
    for child in node_iter:
        if skip is not None and skip(child):
            continue
        if child in path_set:
            cycles.append(path[path.index(child):] + [child])
            continue
        if child not in finished:
            return child
    return None


def dfs_iterative(start, get_deps, skip=None):
    """Обход графа в глубину без рекурсии, с поиском циклов.

    Возвращает порядок обхода и найденные циклы (каждый цикл —
    список вершин, начинающийся и заканчивающийся одной вершиной).
    Вершины, для которых skip вернул истину, пропускаются.
    """
    order = []
    cycles = []
    finished = set()
    path = []
    path_set = set()
    iters = {}
    if skip is not None and skip(start):
        return order, cycles
    stack = [start]
    while stack:
        node = stack[-1]
        if node in finished:
            stack.pop()
            continue
        if node not in iters:
            _enter(node, iters, get_deps, path, path_set, order)
        child = _take_child(iters[node], finished, path,
                            path_set, skip, cycles)
        if child is None:
            _leave(node, stack, finished, path, path_set)
        else:
            stack.append(child)
    return order, cycles
