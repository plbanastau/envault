"""Key aliasing — map a short alias to a full secret key name."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class AliasError(Exception):
    """Raised when an alias operation fails."""


def _aliases_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".aliases.json")


def _load(vault_path: str) -> Dict[str, str]:
    path = _aliases_path(vault_path)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save(vault_path: str, data: Dict[str, str]) -> None:
    path = _aliases_path(vault_path)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)


def set_alias(vault_path: str, alias: str, key: str) -> None:
    """Create or update *alias* so it resolves to *key*."""
    if not alias:
        raise AliasError("Alias name must not be empty.")
    if not key:
        raise AliasError("Target key must not be empty.")
    if alias == key:
        raise AliasError("Alias and target key must differ.")
    data = _load(vault_path)
    data[alias] = key
    _save(vault_path, data)


def remove_alias(vault_path: str, alias: str) -> bool:
    """Delete *alias*. Returns True if it existed, False otherwise."""
    data = _load(vault_path)
    if alias not in data:
        return False
    del data[alias]
    _save(vault_path, data)
    return True


def resolve(vault_path: str, alias: str) -> Optional[str]:
    """Return the key that *alias* maps to, or None if unknown."""
    return _load(vault_path).get(alias)


def list_aliases(vault_path: str) -> List[Dict[str, str]]:
    """Return all aliases sorted by alias name."""
    data = _load(vault_path)
    return [{"alias": a, "key": k} for a, k in sorted(data.items())]


def reverse_lookup(vault_path: str, key: str) -> List[str]:
    """Return every alias that points to *key*."""
    data = _load(vault_path)
    return sorted(alias for alias, target in data.items() if target == key)
