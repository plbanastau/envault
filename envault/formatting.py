"""Value formatting rules for secrets in envault."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

FORMAT_FILE = ".envault_formats.json"

SUPPORTED_FORMATS = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "base64_check": None,  # validation-only, no transform
    "json_check": None,
    "url_check": None,
}


class FormattingError(Exception):
    pass


def _formats_path(vault_path: str) -> Path:
    return Path(vault_path).parent / FORMAT_FILE


def _load(vault_path: str) -> dict:
    p = _formats_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _formats_path(vault_path).write_text(json.dumps(data, indent=2))


def set_format(vault_path: str, key: str, fmt: str) -> str:
    """Assign a named format rule to a key."""
    if not key:
        raise FormattingError("Key must not be empty.")
    if fmt not in SUPPORTED_FORMATS:
        raise FormattingError(
            f"Unknown format '{fmt}'. Supported: {sorted(SUPPORTED_FORMATS)}"
        )
    data = _load(vault_path)
    data[key] = fmt
    _save(vault_path, data)
    return fmt


def get_format(vault_path: str, key: str) -> Optional[str]:
    """Return the format rule assigned to *key*, or None."""
    return _load(vault_path).get(key)


def remove_format(vault_path: str, key: str) -> bool:
    """Remove the format rule for *key*. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_formats(vault_path: str) -> dict[str, str]:
    """Return all key -> format mappings."""
    return dict(_load(vault_path))


def apply_format(value: str, fmt: str) -> str:
    """Apply *fmt* to *value*, raising FormattingError on validation failure."""
    if fmt == "upper":
        return value.upper()
    if fmt == "lower":
        return value.lower()
    if fmt == "strip":
        return value.strip()
    if fmt == "base64_check":
        import base64
        try:
            base64.b64decode(value, validate=True)
        except Exception:
            raise FormattingError(f"Value is not valid base64.")
        return value
    if fmt == "json_check":
        try:
            json.loads(value)
        except json.JSONDecodeError as exc:
            raise FormattingError(f"Value is not valid JSON: {exc}")
        return value
    if fmt == "url_check":
        if not re.match(r'^https?://', value):
            raise FormattingError("Value does not look like an HTTP/HTTPS URL.")
        return value
    raise FormattingError(f"Unknown format '{fmt}'.")
