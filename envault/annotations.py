"""Annotations module — attach free-form notes to secret keys in a vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class AnnotationError(Exception):
    """Raised when an annotation operation fails."""


def _annotations_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault" / "annotations.json"


def _load(vault_path: str) -> dict:
    p = _annotations_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    p = _annotations_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_annotation(vault_path: str, key: str, note: str) -> str:
    """Attach *note* to *key*.  Returns the stored note."""
    if not key:
        raise AnnotationError("key must not be empty")
    if not note:
        raise AnnotationError("note must not be empty")
    data = _load(vault_path)
    data[key] = note
    _save(vault_path, data)
    return note


def get_annotation(vault_path: str, key: str) -> Optional[str]:
    """Return the annotation for *key*, or ``None`` if not set."""
    return _load(vault_path).get(key)


def remove_annotation(vault_path: str, key: str) -> bool:
    """Remove the annotation for *key*.  Returns ``True`` if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_annotations(vault_path: str) -> dict[str, str]:
    """Return all annotations as a ``{key: note}`` mapping, sorted by key."""
    return dict(sorted(_load(vault_path).items()))
