"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = ".envault_audit.json"


def _audit_path(vault_path: str) -> Path:
    """Return the audit log path alongside the vault file."""
    return Path(vault_path).parent / AUDIT_FILENAME


def record(vault_path: str, action: str, key: str, actor: Optional[str] = None) -> None:
    """Append an audit entry for the given action and key."""
    path = _audit_path(vault_path)
    entries = _load_entries(path)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    entries.append(entry)

    path.write_text(json.dumps(entries, indent=2))


def get_log(vault_path: str) -> list[dict]:
    """Return all audit entries for the given vault."""
    path = _audit_path(vault_path)
    return _load_entries(path)


def clear_log(vault_path: str) -> None:
    """Remove the audit log file for the given vault."""
    path = _audit_path(vault_path)
    if path.exists():
        path.unlink()


def _load_entries(path: Path) -> list[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []
