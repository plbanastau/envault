"""Dependency tracking between secrets.

Allows marking that one secret depends on another, enabling
impact analysis when a secret is changed or deleted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


class DependencyError(Exception):
    """Raised when a dependency operation fails."""


def _deps_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".dependencies.json")


def _load(vault_path: str) -> dict:
    p = _deps_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _deps_path(vault_path).write_text(json.dumps(data, indent=2))


def add_dependency(vault_path: str, key: str, depends_on: str) -> None:
    """Record that *key* depends on *depends_on*."""
    if not key:
        raise DependencyError("key must not be empty")
    if not depends_on:
        raise DependencyError("depends_on must not be empty")
    if key == depends_on:
        raise DependencyError("a secret cannot depend on itself")
    data = _load(vault_path)
    deps: List[str] = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
        deps.sort()
    _save(vault_path, data)


def remove_dependency(vault_path: str, key: str, depends_on: str) -> bool:
    """Remove a dependency. Returns True if it existed, False otherwise."""
    data = _load(vault_path)
    deps: List[str] = data.get(key, [])
    if depends_on not in deps:
        return False
    deps.remove(depends_on)
    if not deps:
        del data[key]
    _save(vault_path, data)
    return True


def get_dependencies(vault_path: str, key: str) -> List[str]:
    """Return all keys that *key* directly depends on."""
    return list(_load(vault_path).get(key, []))


def get_dependents(vault_path: str, key: str) -> List[str]:
    """Return all keys that directly depend on *key*."""
    data = _load(vault_path)
    return sorted(k for k, deps in data.items() if key in deps)


def list_all(vault_path: str) -> dict:
    """Return the full dependency map."""
    return dict(_load(vault_path))
