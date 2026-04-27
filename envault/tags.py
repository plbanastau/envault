"""Tag management for envault secrets.

Allows keys to be labeled with one or more tags (e.g. 'prod', 'db', 'ci')
so that users can filter, export, or operate on logical groups of secrets.
"""

from __future__ import annotations

from typing import Dict, List

TAGS_META_KEY = "__tags__"


class TagsError(Exception):
    """Raised when a tag operation cannot be completed."""


def _load_tags(vault) -> Dict[str, List[str]]:
    """Return the tag mapping stored inside the vault (key -> list[tag])."""
    raw = vault.get(TAGS_META_KEY)
    if raw is None:
        return {}
    import json
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def _save_tags(vault, mapping: Dict[str, List[str]], password: str) -> None:
    """Persist the tag mapping back into the vault."""
    import json
    vault.set(TAGS_META_KEY, json.dumps(mapping), password)


def add_tag(vault, key: str, tag: str, password: str) -> None:
    """Add *tag* to *key*.  No-op if the tag is already present."""
    if not key or not tag:
        raise TagsError("key and tag must be non-empty strings")
    if key == TAGS_META_KEY:
        raise TagsError(f"'{TAGS_META_KEY}' is reserved and cannot be tagged")
    mapping = _load_tags(vault)
    tags = mapping.setdefault(key, [])
    if tag not in tags:
        tags.append(tag)
        tags.sort()
        _save_tags(vault, mapping, password)


def remove_tag(vault, key: str, tag: str, password: str) -> bool:
    """Remove *tag* from *key*.  Returns True if removed, False if not found."""
    mapping = _load_tags(vault)
    tags = mapping.get(key, [])
    if tag not in tags:
        return False
    tags.remove(tag)
    if not tags:
        del mapping[key]
    _save_tags(vault, mapping, password)
    return True


def get_tags(vault, key: str) -> List[str]:
    """Return the sorted list of tags for *key* (empty list if none)."""
    return _load_tags(vault).get(key, [])


def keys_for_tag(vault, tag: str) -> List[str]:
    """Return all keys that carry *tag*, sorted alphabetically."""
    mapping = _load_tags(vault)
    return sorted(k for k, tags in mapping.items() if tag in tags)


def all_tags(vault) -> List[str]:
    """Return a sorted list of every distinct tag present in the vault."""
    mapping = _load_tags(vault)
    seen = {t for tags in mapping.values() for t in tags}
    return sorted(seen)
