"""Attach and retrieve arbitrary metadata key-value pairs for vault secrets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MetadataError(Exception):
    """Raised when a metadata operation fails."""


def _metadata_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ".envault" / "metadata.json"


def _load(vault_path: str) -> dict[str, dict[str, Any]]:
    path = _metadata_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: str, data: dict[str, dict[str, Any]]) -> None:
    path = _metadata_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_meta(vault_path: str, key: str, field: str, value: Any) -> dict[str, Any]:
    """Set a metadata field for *key*. Returns the updated metadata dict."""
    if not key:
        raise MetadataError("key must not be empty")
    if not field:
        raise MetadataError("field must not be empty")
    data = _load(vault_path)
    entry = data.setdefault(key, {})
    entry[field] = value
    _save(vault_path, data)
    return dict(entry)


def get_meta(vault_path: str, key: str, field: str) -> Any:
    """Return the value of *field* for *key*, or ``None`` if absent."""
    if not key:
        raise MetadataError("key must not be empty")
    if not field:
        raise MetadataError("field must not be empty")
    return _load(vault_path).get(key, {}).get(field)


def get_all_meta(vault_path: str, key: str) -> dict[str, Any]:
    """Return all metadata fields for *key* (empty dict if none set)."""
    if not key:
        raise MetadataError("key must not be empty")
    return dict(_load(vault_path).get(key, {}))


def remove_meta(vault_path: str, key: str, field: str) -> bool:
    """Remove *field* from *key*'s metadata. Returns True if it existed."""
    if not key:
        raise MetadataError("key must not be empty")
    if not field:
        raise MetadataError("field must not be empty")
    data = _load(vault_path)
    entry = data.get(key, {})
    if field not in entry:
        return False
    del entry[field]
    if not entry:
        data.pop(key, None)
    else:
        data[key] = entry
    _save(vault_path, data)
    return True


def list_meta_keys(vault_path: str) -> list[str]:
    """Return sorted list of secret keys that have metadata attached."""
    return sorted(_load(vault_path).keys())
