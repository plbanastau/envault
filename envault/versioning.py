"""Secret versioning — store and retrieve historical values for vault keys."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class VersioningError(Exception):
    """Raised when a versioning operation fails."""


def _versions_path(vault_path: str | Path) -> Path:
    return Path(vault_path).parent / ".envault" / "versions.json"


def _load(vault_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    p = _versions_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str | Path, data: dict[str, list[dict[str, Any]]]) -> None:
    p = _versions_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def record_version(
    vault_path: str | Path,
    key: str,
    encrypted_value: str,
    actor: str = "system",
) -> dict[str, Any]:
    """Append a new version entry for *key* and return it."""
    if not key:
        raise VersioningError("key must not be empty")
    data = _load(vault_path)
    entry: dict[str, Any] = {
        "version": len(data.get(key, [])) + 1,
        "encrypted_value": encrypted_value,
        "timestamp": time.time(),
        "actor": actor,
    }
    data.setdefault(key, []).append(entry)
    _save(vault_path, data)
    return entry


def list_versions(
    vault_path: str | Path, key: str
) -> list[dict[str, Any]]:
    """Return all recorded versions for *key*, oldest first."""
    return list(_load(vault_path).get(key, []))


def get_version(
    vault_path: str | Path, key: str, version: int
) -> dict[str, Any]:
    """Return a specific version entry (1-based) for *key*."""
    versions = list_versions(vault_path, key)
    if not versions:
        raise VersioningError(f"no versions recorded for key '{key}'")
    if version < 1 or version > len(versions):
        raise VersioningError(
            f"version {version} out of range (1-{len(versions)}) for key '{key}'"
        )
    return versions[version - 1]


def purge_versions(vault_path: str | Path, key: str) -> int:
    """Delete all version history for *key*. Returns the count removed."""
    data = _load(vault_path)
    removed = len(data.pop(key, []))
    _save(vault_path, data)
    return removed
