"""Group management for envault secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class GroupingError(Exception):
    """Raised when a grouping operation fails."""


def _groups_path(vault_path: Path) -> Path:
    return vault_path.parent / f".{vault_path.stem}.groups.json"


def _load(vault_path: Path) -> Dict[str, List[str]]:
    path = _groups_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _groups_path(vault_path).write_text(json.dumps(data, indent=2))


def add_to_group(vault_path: Path, group: str, key: str) -> None:
    """Add a secret key to a named group."""
    if not group.strip():
        raise GroupingError("Group name must not be empty.")
    if not key.strip():
        raise GroupingError("Key must not be empty.")
    data = _load(vault_path)
    members = data.setdefault(group, [])
    if key not in members:
        members.append(key)
        members.sort()
    _save(vault_path, data)


def remove_from_group(vault_path: Path, group: str, key: str) -> bool:
    """Remove a key from a group. Returns True if removed, False if not found."""
    data = _load(vault_path)
    members = data.get(group, [])
    if key not in members:
        return False
    members.remove(key)
    if not members:
        del data[group]
    _save(vault_path, data)
    return True


def get_group(vault_path: Path, group: str) -> List[str]:
    """Return all keys in a group, sorted alphabetically."""
    return _load(vault_path).get(group, [])


def list_groups(vault_path: Path) -> List[str]:
    """Return all group names, sorted alphabetically."""
    return sorted(_load(vault_path).keys())


def delete_group(vault_path: Path, group: str) -> bool:
    """Delete an entire group. Returns True if deleted, False if not found."""
    data = _load(vault_path)
    if group not in data:
        return False
    del data[group]
    _save(vault_path, data)
    return True


def groups_for_key(vault_path: Path, key: str) -> List[str]:
    """Return all groups that contain the given key."""
    data = _load(vault_path)
    return sorted(g for g, members in data.items() if key in members)
