"""Deprecation warnings for renamed or removed secret keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class DeprecationError(Exception):
    """Raised when a deprecation operation fails."""


def _deprecation_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault" / "deprecations.json"


def _load(vault_path: str) -> Dict[str, dict]:
    p = _deprecation_path(vault_path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save(vault_path: str, data: Dict[str, dict]) -> None:
    p = _deprecation_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def mark_deprecated(
    vault_path: str,
    key: str,
    reason: str,
    replacement: Optional[str] = None,
) -> dict:
    """Mark a secret key as deprecated with an optional replacement."""
    if not key:
        raise DeprecationError("key must not be empty")
    if not reason:
        raise DeprecationError("reason must not be empty")

    data = _load(vault_path)
    entry = {"reason": reason, "replacement": replacement}
    data[key] = entry
    _save(vault_path, data)
    return entry


def unmark_deprecated(vault_path: str, key: str) -> bool:
    """Remove a deprecation notice for a key. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def get_deprecation(vault_path: str, key: str) -> Optional[dict]:
    """Return the deprecation entry for a key, or None if not deprecated."""
    return _load(vault_path).get(key)


def list_deprecated(vault_path: str) -> List[dict]:
    """Return all deprecated keys sorted alphabetically."""
    data = _load(vault_path)
    return [
        {"key": k, **v}
        for k, v in sorted(data.items())
    ]


def is_deprecated(vault_path: str, key: str) -> bool:
    """Return True if the key has a deprecation notice."""
    return key in _load(vault_path)
