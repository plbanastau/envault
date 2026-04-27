"""Snapshot support: capture and restore vault state at a point in time."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import Vault


class SnapshotError(Exception):
    """Raised when snapshot operations fail."""


def _snapshot_dir(vault_path: Path) -> Path:
    """Return the directory where snapshots for a vault are stored."""
    return vault_path.parent / ".envault_snapshots" / vault_path.stem


def create_snapshot(vault: Vault, password: str, label: Optional[str] = None) -> str:
    """Capture the current decrypted state of *vault* and persist it.

    Returns the snapshot ID (timestamp-based).
    """
    snapshot_id = str(int(time.time() * 1000))
    snap_dir = _snapshot_dir(vault.path)
    snap_dir.mkdir(parents=True, exist_ok=True)

    secrets: Dict[str, str] = {}
    for key in vault.list_keys():
        value = vault.get(key, password)
        if value is not None:
            secrets[key] = value

    entry = {
        "id": snapshot_id,
        "label": label or "",
        "created_at": time.time(),
        "secrets": secrets,
    }

    snap_file = snap_dir / f"{snapshot_id}.json"
    snap_file.write_text(json.dumps(entry, indent=2))
    return snapshot_id


def list_snapshots(vault_path: Path) -> List[Dict]:
    """Return metadata (id, label, created_at) for all snapshots, newest first."""
    snap_dir = _snapshot_dir(vault_path)
    if not snap_dir.exists():
        return []

    entries = []
    for snap_file in sorted(snap_dir.glob("*.json"), reverse=True):
        data = json.loads(snap_file.read_text())
        entries.append({k: data[k] for k in ("id", "label", "created_at")})
    return entries


def restore_snapshot(vault: Vault, password: str, snapshot_id: str) -> int:
    """Restore vault secrets from *snapshot_id*, overwriting current values.

    Returns the number of keys restored.
    """
    snap_dir = _snapshot_dir(vault.path)
    snap_file = snap_dir / f"{snapshot_id}.json"

    if not snap_file.exists():
        raise SnapshotError(f"Snapshot '{snapshot_id}' not found.")

    data = json.loads(snap_file.read_text())
    secrets: Dict[str, str] = data.get("secrets", {})

    for key, value in secrets.items():
        vault.set(key, value, password)

    return len(secrets)


def delete_snapshot(vault_path: Path, snapshot_id: str) -> bool:
    """Delete a snapshot file. Returns True if deleted, False if not found."""
    snap_file = _snapshot_dir(vault_path) / f"{snapshot_id}.json"
    if snap_file.exists():
        snap_file.unlink()
        return True
    return False
