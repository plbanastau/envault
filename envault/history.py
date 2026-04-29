"""Track value change history for individual keys in a vault."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional


class HistoryError(Exception):
    """Raised when a history operation fails."""


def _history_path(vault_path: str) -> Path:
    base = Path(vault_path)
    return base.parent / (base.stem + ".history.json")


def _load(vault_path: str) -> dict:
    p = _history_path(vault_path)
    if not p.exists():
        return {}
    with p.open("r") as f:
        return json.load(f)


def _save(vault_path: str, data: dict) -> None:
    p = _history_path(vault_path)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def record_change(vault_path: str, key: str, new_value: str, actor: str = "cli") -> None:
    """Record that *key* was set to *new_value* at the current time."""
    if not key:
        raise HistoryError("Key must not be empty.")
    data = _load(vault_path)
    entries = data.get(key, [])
    entries.append({
        "timestamp": time.time(),
        "actor": actor,
        "value_preview": new_value[:4] + "****" if len(new_value) > 4 else "****",
    })
    data[key] = entries
    _save(vault_path, data)


def get_history(vault_path: str, key: str) -> List[dict]:
    """Return the list of change records for *key*, oldest first."""
    if not key:
        raise HistoryError("Key must not be empty.")
    data = _load(vault_path)
    return list(data.get(key, []))


def clear_history(vault_path: str, key: Optional[str] = None) -> None:
    """Clear history for a specific key, or all keys if *key* is None."""
    data = _load(vault_path)
    if key is None:
        data = {}
    elif key in data:
        del data[key]
    _save(vault_path, data)


def list_tracked_keys(vault_path: str) -> List[str]:
    """Return sorted list of keys that have at least one history entry."""
    data = _load(vault_path)
    return sorted(data.keys())
