"""Key remapping — define aliases that map one key name to another at export time."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class RemappingError(Exception):
    """Raised when a remapping operation fails."""


def _remapping_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".remapping.json")


def _load(vault_path: str) -> Dict[str, str]:
    p = _remapping_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, str]) -> None:
    _remapping_path(vault_path).write_text(json.dumps(data, indent=2, sort_keys=True))


def set_remap(vault_path: str, key: str, target: str) -> Dict[str, str]:
    """Map *key* to *target* name during export."""
    if not key:
        raise RemappingError("key must not be empty")
    if not target:
        raise RemappingError("target must not be empty")
    data = _load(vault_path)
    data[key] = target
    _save(vault_path, data)
    return {"key": key, "target": target}


def get_remap(vault_path: str, key: str) -> Optional[str]:
    """Return the remapped name for *key*, or None if not set."""
    return _load(vault_path).get(key)


def remove_remap(vault_path: str, key: str) -> bool:
    """Remove the remapping for *key*. Returns True if removed, False if absent."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_remaps(vault_path: str) -> Dict[str, str]:
    """Return all current key→target remappings."""
    return dict(sorted(_load(vault_path).items()))


def apply_remaps(vault_path: str, secrets: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of *secrets* with remapped keys applied.

    Keys that have no remapping are kept under their original name.
    If a remapped target name collides with an existing key, the remapped
    entry takes precedence.
    """
    mapping = _load(vault_path)
    result: Dict[str, str] = {}
    for key, value in secrets.items():
        out_key = mapping.get(key, key)
        result[out_key] = value
    return result
