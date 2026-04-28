"""Template rendering for environment variable sets.

Allows defining named templates (collections of keys with optional default
values) that can be applied to a vault to scaffold new environments quickly.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class TemplateError(Exception):
    """Raised when a template operation fails."""


def _templates_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".templates.json")


def _load(vault_path: str) -> Dict[str, Dict[str, str]]:
    path = _templates_path(vault_path)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save(vault_path: str, data: Dict[str, Dict[str, str]]) -> None:
    path = _templates_path(vault_path)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def save_template(vault_path: str, name: str, keys: Dict[str, str]) -> None:
    """Save a named template mapping key names to default values."""
    if not name:
        raise TemplateError("Template name must not be empty.")
    data = _load(vault_path)
    data[name] = {k: v for k, v in keys.items()}
    _save(vault_path, data)


def get_template(vault_path: str, name: str) -> Dict[str, str]:
    """Return the key->default mapping for a template, or raise TemplateError."""
    data = _load(vault_path)
    if name not in data:
        raise TemplateError(f"Template '{name}' not found.")
    return dict(data[name])


def list_templates(vault_path: str) -> List[str]:
    """Return sorted list of template names."""
    return sorted(_load(vault_path).keys())


def delete_template(vault_path: str, name: str) -> bool:
    """Delete a template. Returns True if deleted, False if not found."""
    data = _load(vault_path)
    if name not in data:
        return False
    del data[name]
    _save(vault_path, data)
    return True


def apply_template(
    vault_path: str,
    name: str,
    password: str,
    overwrite: bool = False,
) -> List[str]:
    """Apply a template to a vault, setting missing keys to their defaults.

    Returns the list of keys that were written.
    """
    from envault.vault import Vault  # local import to avoid circular deps

    template = get_template(vault_path, name)
    vault = Vault(vault_path, password)
    written: List[str] = []
    for key, default in template.items():
        if not overwrite and vault.get(key) is not None:
            continue
        vault.set(key, default)
        written.append(key)
    return written
