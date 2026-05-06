"""Key labeling — attach human-readable display labels to secret keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class LabelingError(Exception):
    """Raised when a labeling operation fails."""


def _labels_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault" / "labels.json"


def _load(vault_path: str) -> Dict[str, str]:
    p = _labels_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, str]) -> None:
    p = _labels_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_label(vault_path: str, key: str, label: str) -> str:
    """Attach a display *label* to *key*. Returns the stored label."""
    if not key:
        raise LabelingError("key must not be empty")
    if not label:
        raise LabelingError("label must not be empty")
    data = _load(vault_path)
    data[key] = label
    _save(vault_path, data)
    return label


def get_label(vault_path: str, key: str) -> Optional[str]:
    """Return the display label for *key*, or ``None`` if unset."""
    return _load(vault_path).get(key)


def remove_label(vault_path: str, key: str) -> bool:
    """Remove the label for *key*. Returns ``True`` if a label existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_labels(vault_path: str) -> List[Dict[str, str]]:
    """Return all label entries sorted by key name."""
    data = _load(vault_path)
    return [{"key": k, "label": v} for k, v in sorted(data.items())]


def keys_with_label(vault_path: str, label: str) -> List[str]:
    """Return all keys whose label equals *label* (case-sensitive)."""
    data = _load(vault_path)
    return sorted(k for k, v in data.items() if v == label)
