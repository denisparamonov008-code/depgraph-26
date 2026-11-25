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


def collect_entries(entries, opener, versions, links):
    """Собрать версии и адреса карточек, подгружая страницы."""
    for entry in entries:
        if "items" in entry:
            collect_entries(entry["items"], opener, versions, links)
        elif "catalogEntry" in entry:
            version = entry["catalogEntry"].get("version")
            if version and version not in versions:
                versions.append(version)
            if version and "@id" in entry:
                links[version] = entry["@id"]
        elif "@id" in entry:
            sub = fetch_json(entry["@id"], opener)
            collect_entries(sub.get("items", []), opener,
                            versions, links)
        else:
            version = entry.get("version")
            if version and version not in versions:
                versions.append(version)


def list_versions(registration, opener=None):
    """Вернуть список версий из ответа регистрации."""
    versions = []
    collect_entries(registration.get("items", []), opener,
                    versions, {})
    return versions


def leaf_url(registration, version, opener=None):
    """Найти адрес карточки указанной версии пакета."""
    versions = []
    links = {}
    collect_entries(registration.get("items", []), opener,
                    versions, links)
    return links.get(version)


def leaf_dependencies(leaf, opener=None):
    """Извлечь имена прямых зависимостей из карточки версии."""
    groups = leaf.get("dependencyGroups", [])
    if not groups and isinstance(leaf.get("catalogEntry"), str):
        entry = fetch_json(leaf["catalogEntry"], opener)
        groups = entry.get("dependencyGroups", [])
    names = []
    for group in groups:
        for dep in group.get("dependencies", []):
            dep_id = dep.get("id")
            if dep_id and dep_id not in names:
                names.append(dep_id)
    return names


def resolve_base(repo, opener=None):
    """Определить базовый адрес каталога регистрации."""
    try:
        answer = fetch_json(repo, opener)
    except Exception:
        return repo.rstrip("/")
    if isinstance(answer, dict):
        for res in answer.get("resources", []):
            res_type = res.get("@type", "")
            if "RegistrationsBaseUrl" in res_type:
                return res.get("@id", repo).rstrip("/")
    return repo.rstrip("/")


def direct_dependencies(package, repo_base=None, opener=None):
    """Вернуть прямые зависимости самой свежей версии пакета."""
    base = resolve_base(repo_base or REGISTRATION_BASE, opener)
    index_url = "%s/%s/index.json" % (base, package.lower())
    registration = fetch_json(index_url, opener)
    versions = list_versions(registration, opener)
    stable = [v for v in versions if "-" not in v]
    if stable:
        versions = stable
    if not versions:
        return []
    url = leaf_url(registration, versions[-1], opener)
    if not url:
        return []
    return leaf_dependencies(fetch_json(url, opener), opener)
