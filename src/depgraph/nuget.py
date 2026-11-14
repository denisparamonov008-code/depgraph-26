"""Получение прямых зависимостей пакета NuGet (этап 2).

Используются только стандартные средства Python: адреса берутся
из протокола NuGet V3, запросы выполняются через urllib.
Менеджеры пакетов и сторонние библиотеки не задействованы.
"""

import gzip
import json
import urllib.request

HTTP_TIMEOUT = 20
REGISTRATION_BASE = (
    "https://api.nuget.org/v3/registration5-gz-semver2")


def fetch_json(url, opener=None):
    """Скачать JSON по адресу и разобрать его в словарь."""
    if opener is not None:
        return opener(url)
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
        raw = resp.read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    return json.loads(raw.decode("utf-8"))


def list_versions(registration):
    """Вернуть список версий из ответа регистрации."""
    versions = []
    for page in registration.get("items", []):
        entries = page.get("items", [page])
        for entry in entries:
            inner = entry.get("catalogEntry", entry)
            version = inner.get("version")
            if version and version not in versions:
                versions.append(version)
    return versions


def leaf_url(registration, version):
    """Найти адрес карточки указанной версии пакета."""
    for page in registration.get("items", []):
        entries = page.get("items", [page])
        for entry in entries:
            inner = entry.get("catalogEntry", entry)
            if inner.get("version") == version and "@id" in entry:
                return entry["@id"]
    return None


def leaf_dependencies(leaf):
    """Извлечь имена прямых зависимостей из карточки версии."""
    names = []
    groups = leaf.get("dependencyGroups", [])
    for group in groups:
        for dep in group.get("dependencies", []):
            dep_id = dep.get("id")
            if dep_id and dep_id not in names:
                names.append(dep_id)
    return names


def direct_dependencies(package, repo_base=None, opener=None):
    """Вернуть прямые зависимости самой свежей версии пакета."""
    base = (repo_base or REGISTRATION_BASE).rstrip("/")
    index_url = "%s/%s/index.json" % (base, package.lower())
    registration = fetch_json(index_url, opener)
    versions = list_versions(registration)
    if not versions:
        return []
    url = leaf_url(registration, versions[-1])
    if not url:
        return []
    return leaf_dependencies(fetch_json(url, opener))
