"""TTL (time-to-live) support for individual secrets in a vault."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


class TTLError(Exception):
    """Raised when a TTL operation fails."""


def _ttl_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".ttl.json")


def _load_ttl(vault_path: Path) -> dict:
    path = _ttl_path(vault_path)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_ttl(vault_path: Path, data: dict) -> None:
    path = _ttl_path(vault_path)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_ttl(vault_path: Path, key: str, seconds: int) -> float:
    """Set a TTL for *key*. Returns the absolute expiry timestamp."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    data = _load_ttl(vault_path)
    expires_at = time.time() + seconds
    data[key] = expires_at
    _save_ttl(vault_path, data)
    return expires_at


def get_ttl(vault_path: Path, key: str) -> Optional[float]:
    """Return the expiry timestamp for *key*, or None if no TTL is set."""
    data = _load_ttl(vault_path)
    return data.get(key)


def is_expired(vault_path: Path, key: str) -> bool:
    """Return True if *key* has a TTL that has already passed."""
    expires_at = get_ttl(vault_path, key)
    if expires_at is None:
        return False
    return time.time() >= expires_at


def clear_ttl(vault_path: Path, key: str) -> bool:
    """Remove the TTL for *key*. Returns True if an entry was removed."""
    data = _load_ttl(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_ttl(vault_path, data)
    return True


def purge_expired(vault_path: Path) -> list[str]:
    """Delete all expired TTL entries and return their keys."""
    data = _load_ttl(vault_path)
    now = time.time()
    expired = [k for k, exp in data.items() if now >= exp]
    for k in expired:
        del data[k]
    if expired:
        _save_ttl(vault_path, data)
    return expired
