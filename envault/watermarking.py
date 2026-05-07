"""Watermarking: embed and verify hidden metadata in secret values."""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Optional

WATERMARK_PREFIX = "\u200b"  # zero-width space as invisible separator
_WATERMARK_FILE = ".watermarks.json"


class WatermarkError(Exception):
    """Raised when a watermarking operation fails."""


def _watermarks_path(vault_path: str) -> pathlib.Path:
    return pathlib.Path(vault_path).parent / _WATERMARK_FILE


def _load(vault_path: str) -> dict:
    p = _watermarks_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    p = _watermarks_path(vault_path)
    p.write_text(json.dumps(data, indent=2))


def _fingerprint(key: str, value: str, actor: str) -> str:
    """Produce a short fingerprint tying key, value, and actor together."""
    raw = f"{key}:{value}:{actor}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def embed(vault_path: str, key: str, value: str, actor: str) -> str:
    """Embed a watermark for *key* and return the annotated value.

    The returned string is functionally identical to *value* for most
    consumers; the watermark is stored separately and can be verified
    later with :func:`verify`.
    """
    if not key:
        raise WatermarkError("key must not be empty")
    if not actor:
        raise WatermarkError("actor must not be empty")

    fp = _fingerprint(key, value, actor)
    data = _load(vault_path)
    data[key] = {"actor": actor, "fingerprint": fp}
    _save(vault_path, data)
    return value


def verify(vault_path: str, key: str, value: str) -> Optional[str]:
    """Verify the watermark for *key*/*value*.

    Returns the *actor* string if the fingerprint matches, or ``None``
    if no watermark exists.  Raises :class:`WatermarkError` on
    fingerprint mismatch (tampered value).
    """
    data = _load(vault_path)
    if key not in data:
        return None

    entry = data[key]
    actor = entry["actor"]
    expected = _fingerprint(key, value, actor)
    if entry["fingerprint"] != expected:
        raise WatermarkError(
            f"Watermark verification failed for '{key}': value may have been tampered with"
        )
    return actor


def remove(vault_path: str, key: str) -> bool:
    """Remove the watermark for *key*.  Returns True if one existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_watermarks(vault_path: str) -> dict:
    """Return a mapping of key -> actor for all watermarked secrets."""
    data = _load(vault_path)
    return {k: v["actor"] for k, v in data.items()}
