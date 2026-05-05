"""Scoping module — associate secrets with named scopes (e.g. dev, staging, prod)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ScopingError(Exception):
    """Raised when a scoping operation fails."""


def _scopes_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault_scopes.json"


def _load(vault_path: str) -> Dict[str, List[str]]:
    path = _scopes_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: str, data: Dict[str, List[str]]) -> None:
    _scopes_path(vault_path).write_text(json.dumps(data, indent=2))


def assign_scope(vault_path: str, key: str, scope: str) -> None:
    """Assign *key* to *scope*. A key may belong to multiple scopes."""
    if not key:
        raise ScopingError("Key must not be empty.")
    if not scope:
        raise ScopingError("Scope must not be empty.")
    data = _load(vault_path)
    scopes_for_key = data.setdefault(key, [])
    if scope not in scopes_for_key:
        scopes_for_key.append(scope)
        scopes_for_key.sort()
    _save(vault_path, data)


def remove_scope(vault_path: str, key: str, scope: str) -> bool:
    """Remove *scope* from *key*. Returns True if removed, False if not found."""
    data = _load(vault_path)
    scopes_for_key = data.get(key, [])
    if scope not in scopes_for_key:
        return False
    scopes_for_key.remove(scope)
    if not scopes_for_key:
        del data[key]
    _save(vault_path, data)
    return True


def get_scopes(vault_path: str, key: str) -> List[str]:
    """Return all scopes assigned to *key*."""
    return _load(vault_path).get(key, [])


def keys_in_scope(vault_path: str, scope: str) -> List[str]:
    """Return all keys that belong to *scope*, sorted."""
    data = _load(vault_path)
    return sorted(k for k, scopes in data.items() if scope in scopes)


def list_scopes(vault_path: str) -> List[str]:
    """Return a deduplicated, sorted list of all scope names in use."""
    data = _load(vault_path)
    all_scopes: set = set()
    for scopes in data.values():
        all_scopes.update(scopes)
    return sorted(all_scopes)


def clear_scopes(vault_path: str, key: str) -> None:
    """Remove all scope assignments for *key*."""
    data = _load(vault_path)
    data.pop(key, None)
    _save(vault_path, data)
