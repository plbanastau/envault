"""Profile management for envault — named sets of key filters per environment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ProfilesError(Exception):
    """Raised when a profile operation fails."""


def _profiles_path(vault_path: Path) -> Path:
    return vault_path.parent / f"{vault_path.stem}.profiles.json"


def _load(vault_path: Path) -> Dict[str, List[str]]:
    p = _profiles_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _profiles_path(vault_path).write_text(json.dumps(data, indent=2, sort_keys=True))


def save_profile(vault_path: Path, name: str, keys: List[str]) -> None:
    """Save (create or overwrite) a named profile with the given key list."""
    if not name or not name.strip():
        raise ProfilesError("Profile name must not be empty.")
    if not keys:
        raise ProfilesError("Profile must contain at least one key.")
    data = _load(vault_path)
    data[name] = sorted(set(keys))
    _save(vault_path, data)


def get_profile(vault_path: Path, name: str) -> List[str]:
    """Return the key list for a named profile."""
    data = _load(vault_path)
    if name not in data:
        raise ProfilesError(f"Profile '{name}' does not exist.")
    return data[name]


def list_profiles(vault_path: Path) -> List[str]:
    """Return all profile names, sorted alphabetically."""
    return sorted(_load(vault_path).keys())


def delete_profile(vault_path: Path, name: str) -> bool:
    """Delete a profile. Returns True if deleted, False if it did not exist."""
    data = _load(vault_path)
    if name not in data:
        return False
    del data[name]
    _save(vault_path, data)
    return True


def rename_profile(vault_path: Path, old_name: str, new_name: str) -> None:
    """Rename an existing profile."""
    if not new_name or not new_name.strip():
        raise ProfilesError("New profile name must not be empty.")
    data = _load(vault_path)
    if old_name not in data:
        raise ProfilesError(f"Profile '{old_name}' does not exist.")
    if new_name in data:
        raise ProfilesError(f"Profile '{new_name}' already exists.")
    data[new_name] = data.pop(old_name)
    _save(vault_path, data)
