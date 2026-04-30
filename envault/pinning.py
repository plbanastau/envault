"""envault.pinning — Pin secrets to specific versions and retrieve pinned values."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.vault import Vault


class PinningError(Exception):
    """Raised when a pinning operation fails."""


def _pins_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".pins.json")


def _load(vault_path: Path) -> dict:
    p = _pins_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: dict) -> None:
    _pins_path(vault_path).write_text(json.dumps(data, indent=2))


def pin_secret(vault_path: Path, password: str, key: str, label: str) -> dict:
    """Pin the current encrypted value of *key* under *label*.

    Returns the new pin entry.
    """
    if not label:
        raise PinningError("Pin label must not be empty.")

    vault = Vault(vault_path, password)
    raw_value = vault.get(key)
    if raw_value is None:
        raise PinningError(f"Key '{key}' not found in vault.")

    data = _load(vault_path)
    pins_for_key = data.setdefault(key, {})
    if label in pins_for_key:
        raise PinningError(f"Pin '{label}' already exists for key '{key}'.")

    entry = {
        "label": label,
        "value": raw_value,
        "pinned_at": datetime.now(timezone.utc).isoformat(),
    }
    pins_for_key[label] = entry
    _save(vault_path, data)
    return entry


def get_pin(vault_path: Path, key: str, label: str) -> Optional[str]:
    """Return the pinned plaintext value for *key* / *label*, or None."""
    data = _load(vault_path)
    entry = data.get(key, {}).get(label)
    if entry is None:
        return None
    return entry["value"]


def list_pins(vault_path: Path, key: str) -> list[dict]:
    """Return all pin entries for *key*, sorted by pinned_at ascending."""
    data = _load(vault_path)
    entries = list(data.get(key, {}).values())
    return sorted(entries, key=lambda e: e["pinned_at"])


def delete_pin(vault_path: Path, key: str, label: str) -> bool:
    """Delete a pin. Returns True if deleted, False if it did not exist."""
    data = _load(vault_path)
    pins_for_key = data.get(key, {})
    if label not in pins_for_key:
        return False
    del pins_for_key[label]
    if not pins_for_key:
        data.pop(key, None)
    _save(vault_path, data)
    return True
