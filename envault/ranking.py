"""Secret ranking — score and rank vault keys by usage, age, and access frequency."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RANKING_FILE = ".envault_ranking.json"


class RankingError(Exception):
    """Raised when a ranking operation fails."""


def _ranking_path(vault_path: str) -> Path:
    return Path(vault_path).parent / RANKING_FILE


def _load(vault_path: str) -> dict[str, Any]:
    path = _ranking_path(vault_path)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save(vault_path: str, data: dict[str, Any]) -> None:
    path = _ranking_path(vault_path)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def record_access(vault_path: str, key: str) -> int:
    """Increment the access counter for *key* and return the new count."""
    if not key:
        raise RankingError("key must not be empty")
    data = _load(vault_path)
    entry = data.get(key, {"access_count": 0})
    entry["access_count"] = entry.get("access_count", 0) + 1
    data[key] = entry
    _save(vault_path, data)
    return entry["access_count"]


def get_score(vault_path: str, key: str) -> int:
    """Return the current access score for *key* (0 if never accessed)."""
    if not key:
        raise RankingError("key must not be empty")
    data = _load(vault_path)
    return data.get(key, {}).get("access_count", 0)


def ranked_keys(vault_path: str) -> list[tuple[str, int]]:
    """Return all tracked keys sorted by access count descending."""
    data = _load(vault_path)
    pairs = [(k, v.get("access_count", 0)) for k, v in data.items()]
    return sorted(pairs, key=lambda x: x[1], reverse=True)


def reset_score(vault_path: str, key: str) -> bool:
    """Reset the access counter for *key*. Returns True if the key existed."""
    if not key:
        raise RankingError("key must not be empty")
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True
