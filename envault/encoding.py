"""encoding.py — Per-key value encoding format registry (base64, hex, utf8)."""

from __future__ import annotations

import base64
import json
from pathlib import Path

ENCODING_FILE = ".encoding.json"

SUPPORTED_ENCODINGS = ("utf8", "base64", "hex")


class EncodingError(Exception):
    """Raised when an encoding operation fails."""


def _encoding_path(vault_path: str | Path) -> Path:
    return Path(vault_path).parent / ENCODING_FILE


def _load(vault_path: str | Path) -> dict:
    p = _encoding_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str | Path, data: dict) -> None:
    _encoding_path(vault_path).write_text(json.dumps(data, indent=2))


def set_encoding(vault_path: str | Path, key: str, encoding: str) -> str:
    """Assign an encoding format to *key*. Returns the encoding name."""
    if not key:
        raise EncodingError("key must not be empty")
    if encoding not in SUPPORTED_ENCODINGS:
        raise EncodingError(
            f"unsupported encoding '{encoding}'; choose from {SUPPORTED_ENCODINGS}"
        )
    data = _load(vault_path)
    data[key] = encoding
    _save(vault_path, data)
    return encoding


def get_encoding(vault_path: str | Path, key: str) -> str | None:
    """Return the encoding assigned to *key*, or None if unset."""
    return _load(vault_path).get(key)


def remove_encoding(vault_path: str | Path, key: str) -> bool:
    """Remove encoding for *key*. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def encode_value(value: str, encoding: str) -> str:
    """Encode *value* using the specified encoding."""
    if encoding == "utf8":
        return value
    if encoding == "base64":
        return base64.b64encode(value.encode()).decode()
    if encoding == "hex":
        return value.encode().hex()
    raise EncodingError(f"unknown encoding '{encoding}'")


def decode_value(value: str, encoding: str) -> str:
    """Decode *value* using the specified encoding."""
    if encoding == "utf8":
        return value
    if encoding == "base64":
        return base64.b64decode(value.encode()).decode()
    if encoding == "hex":
        return bytes.fromhex(value).decode()
    raise EncodingError(f"unknown encoding '{encoding}'")
