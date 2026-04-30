"""Secret expiry management — set, check, and list expiring secrets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


class ExpiryError(Exception):
    """Raised when an expiry operation fails."""


def _expiry_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".expiry.json")


def _load(vault_path: Path) -> dict:
    p = _expiry_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: dict) -> None:
    _expiry_path(vault_path).write_text(json.dumps(data, indent=2))


def set_expiry(vault_path: Path, key: str, expires_at: datetime) -> str:
    """Set an expiry datetime for *key*. Returns the stored ISO timestamp."""
    if not key:
        raise ExpiryError("Key must not be empty.")
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    data = _load(vault_path)
    ts = expires_at.strftime(DATE_FMT)
    data[key] = ts
    _save(vault_path, data)
    return ts


def get_expiry(vault_path: Path, key: str) -> Optional[datetime]:
    """Return the expiry datetime for *key*, or ``None`` if not set."""
    data = _load(vault_path)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.strptime(raw, DATE_FMT).replace(tzinfo=timezone.utc)


def is_expired(vault_path: Path, key: str) -> bool:
    """Return ``True`` if *key* has an expiry that is in the past."""
    exp = get_expiry(vault_path, key)
    if exp is None:
        return False
    return datetime.now(tz=timezone.utc) >= exp


def remove_expiry(vault_path: Path, key: str) -> bool:
    """Remove the expiry for *key*. Returns ``True`` if an entry was removed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_expiring(vault_path: Path) -> list[dict]:
    """Return all keys with expiry info, sorted soonest-first."""
    data = _load(vault_path)
    now = datetime.now(tz=timezone.utc)
    entries = []
    for key, raw in data.items():
        exp = datetime.strptime(raw, DATE_FMT).replace(tzinfo=timezone.utc)
        entries.append({"key": key, "expires_at": raw, "expired": now >= exp})
    entries.sort(key=lambda e: e["expires_at"])
    return entries
