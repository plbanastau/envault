"""Policy enforcement for vault access rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

POLICY_FILENAME = ".envault_policy.json"

VALID_RULES = {"require_ttl", "deny_plaintext_export", "max_secret_length", "allowed_key_pattern"}


class PolicyError(Exception):
    """Raised when a policy rule is violated or misconfigured."""


def _policy_path(vault_path: str) -> Path:
    return Path(vault_path).parent / POLICY_FILENAME


def _load(vault_path: str) -> dict[str, Any]:
    path = _policy_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: str, data: dict[str, Any]) -> None:
    _policy_path(vault_path).write_text(json.dumps(data, indent=2))


def set_rule(vault_path: str, rule: str, value: Any) -> None:
    """Set a policy rule for the vault."""
    if rule not in VALID_RULES:
        raise PolicyError(f"Unknown policy rule '{rule}'. Valid rules: {sorted(VALID_RULES)}")
    data = _load(vault_path)
    data[rule] = value
    _save(vault_path, data)


def get_rule(vault_path: str, rule: str) -> Any:
    """Return the value of a policy rule, or None if not set."""
    return _load(vault_path).get(rule)


def list_rules(vault_path: str) -> dict[str, Any]:
    """Return all configured policy rules."""
    return _load(vault_path)


def remove_rule(vault_path: str, rule: str) -> bool:
    """Remove a policy rule. Returns True if it existed."""
    data = _load(vault_path)
    if rule not in data:
        return False
    del data[rule]
    _save(vault_path, data)
    return True


def enforce(vault_path: str, key: str, value: str) -> None:
    """Enforce all applicable policies for a key/value pair.

    Raises PolicyError if any rule is violated.
    """
    import re

    rules = _load(vault_path)

    if "max_secret_length" in rules:
        limit = int(rules["max_secret_length"])
        if len(value) > limit:
            raise PolicyError(
                f"Value for '{key}' exceeds max_secret_length of {limit} characters."
            )

    if "allowed_key_pattern" in rules:
        pattern = rules["allowed_key_pattern"]
        if not re.fullmatch(pattern, key):
            raise PolicyError(
                f"Key '{key}' does not match allowed_key_pattern '{pattern}'."
            )
