"""Vault inheritance: allow one vault to inherit secrets from a parent vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class InheritanceError(Exception):
    """Raised when an inheritance operation fails."""


def _inheritance_path(vault_path: Path) -> Path:
    return vault_path.parent / f"{vault_path.stem}.inheritance.json"


def _load(vault_path: Path) -> Dict:
    p = _inheritance_path(vault_path)
    if not p.exists():
        return {"parent": None, "overrides": []}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: Dict) -> None:
    _inheritance_path(vault_path).write_text(json.dumps(data, indent=2))


def set_parent(vault_path: Path, parent_path: Path) -> None:
    """Register *parent_path* as the parent vault for *vault_path*."""
    resolved = str(parent_path.resolve())
    if str(vault_path.resolve()) == resolved:
        raise InheritanceError("A vault cannot inherit from itself.")
    data = _load(vault_path)
    data["parent"] = resolved
    _save(vault_path, data)


def get_parent(vault_path: Path) -> Optional[Path]:
    """Return the parent vault path, or None if not set."""
    raw = _load(vault_path).get("parent")
    return Path(raw) if raw else None


def clear_parent(vault_path: Path) -> bool:
    """Remove the parent reference. Returns True if one existed."""
    data = _load(vault_path)
    if data.get("parent") is None:
        return False
    data["parent"] = None
    _save(vault_path, data)
    return True


def add_override(vault_path: Path, key: str) -> None:
    """Mark *key* as a local override (never inherited from parent)."""
    if not key:
        raise InheritanceError("Key must not be empty.")
    data = _load(vault_path)
    if key not in data["overrides"]:
        data["overrides"] = sorted(data["overrides"] + [key])
        _save(vault_path, data)


def remove_override(vault_path: Path, key: str) -> bool:
    """Remove *key* from the overrides list. Returns True if it was present."""
    data = _load(vault_path)
    if key not in data["overrides"]:
        return False
    data["overrides"] = [k for k in data["overrides"] if k != key]
    _save(vault_path, data)
    return True


def list_overrides(vault_path: Path) -> List[str]:
    """Return the list of keys that are treated as local overrides."""
    return list(_load(vault_path).get("overrides", []))
