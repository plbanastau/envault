"""Key/value validation rules for envault secrets."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class ValidationError(Exception):
    """Raised when a validation rule is violated."""


@dataclass
class ValidationResult:
    key: str
    passed: bool
    violations: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        status = "OK" if self.passed else "FAIL"
        return f"ValidationResult({self.key!r}, {status}, violations={self.violations})"


_RULES: dict[str, dict] = {
    "non_empty": {"description": "Value must not be empty"},
    "no_whitespace": {"description": "Value must not contain leading/trailing whitespace"},
    "printable_ascii": {"description": "Value must contain only printable ASCII characters"},
    "min_length": {"description": "Value must meet minimum length", "param": "min"},
    "max_length": {"description": "Value must not exceed maximum length", "param": "max"},
    "regex": {"description": "Value must match a regular expression", "param": "pattern"},
}


def available_rules() -> List[str]:
    """Return the list of built-in rule names."""
    return list(_RULES.keys())


def validate_value(key: str, value: str, rules: List[dict]) -> ValidationResult:
    """Apply *rules* to *value* and return a :class:`ValidationResult`.

    Each rule dict must contain a ``"rule"`` key naming the rule, plus any
    rule-specific parameters (e.g. ``{"rule": "min_length", "min": 8}``).
    """
    if not isinstance(value, str):
        raise ValidationError(f"value for key {key!r} must be a string, got {type(value).__name__}")

    violations: List[str] = []

    for spec in rules:
        name = spec.get("rule")
        if name not in _RULES:
            raise ValidationError(f"Unknown validation rule: {name!r}")

        if name == "non_empty" and value == "":
            violations.append("Value must not be empty.")

        elif name == "no_whitespace" and value != value.strip():
            violations.append("Value must not contain leading/trailing whitespace.")

        elif name == "printable_ascii" and not all(32 <= ord(c) <= 126 for c in value):
            violations.append("Value must contain only printable ASCII characters.")

        elif name == "min_length":
            min_len = int(spec.get("min", 0))
            if len(value) < min_len:
                violations.append(f"Value length {len(value)} is below minimum {min_len}.")

        elif name == "max_length":
            max_len = int(spec.get("max", 0))
            if len(value) > max_len:
                violations.append(f"Value length {len(value)} exceeds maximum {max_len}.")

        elif name == "regex":
            pattern = spec.get("pattern", "")
            if not re.search(pattern, value):
                violations.append(f"Value does not match pattern {pattern!r}.")

    return ValidationResult(key=key, passed=len(violations) == 0, violations=violations)
