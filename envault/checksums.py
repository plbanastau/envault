"""Checksum tracking for vault secrets — detects unexpected external modifications."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional


class ChecksumError(Exception):
    """Raised when a checksum operation fails."""


def _checksums_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault" / "checksums.json"


def _load(vault_path: str) -> Dict[str, str]:
    p = _checksums_path(vault_path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save(vault_path: str, data: Dict[str, str]) -> None:
    p = _checksums_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def _hash(value: str) -> str:
    """Return a SHA-256 hex digest of the given string value."""
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_path: str, key: str, value: str) -> str:
    """Store a checksum for *key* based on *value*. Returns the digest."""
    if not key:
        raise ChecksumError("key must not be empty")
    data = _load(vault_path)
    digest = _hash(value)
    data[key] = digest
    _save(vault_path, data)
    return digest


def get_checksum(vault_path: str, key: str) -> Optional[str]:
    """Return the stored checksum for *key*, or None if not recorded."""
    return _load(vault_path).get(key)


def verify_checksum(vault_path: str, key: str, value: str) -> bool:
    """Return True if *value* matches the stored checksum for *key*."""
    stored = get_checksum(vault_path, key)
    if stored is None:
        return False
    return stored == _hash(value)


def delete_checksum(vault_path: str, key: str) -> bool:
    """Remove the checksum entry for *key*. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_checksums(vault_path: str) -> Dict[str, str]:
    """Return a copy of all stored {key: digest} pairs."""
    return dict(_load(vault_path))
