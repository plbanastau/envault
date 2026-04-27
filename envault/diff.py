"""Diff two vault snapshots or a snapshot against the current vault state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.vault import Vault
from envault.snapshot import restore_snapshot, SnapshotError


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def diff_dicts(
    old: Dict[str, str],
    new: Dict[str, str],
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two plaintext secret dicts and return a list of DiffEntry objects."""
    entries: List[DiffEntry] = []
    all_keys = sorted(set(old) | set(new))

    for key in all_keys:
        in_old = key in old
        in_new = key in new

        if in_old and not in_new:
            entries.append(DiffEntry(key=key, status="removed", old_value=old[key]))
        elif in_new and not in_old:
            entries.append(DiffEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(
                DiffEntry(key=key, status="changed", old_value=old[key], new_value=new[key])
            )
        elif show_unchanged:
            entries.append(
                DiffEntry(key=key, status="unchanged", old_value=old[key], new_value=new[key])
            )

    return entries


def diff_snapshot_vs_current(
    vault: Vault,
    snapshot_id: str,
    password: str,
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Diff a named snapshot against the current vault state."""
    snap_vault = restore_snapshot(vault.path, snapshot_id, password, dry_run=True)
    old_secrets = {k: snap_vault.get(k, password) for k in snap_vault.keys()}
    new_secrets = {k: vault.get(k, password) for k in vault.keys()}
    return diff_dicts(old_secrets, new_secrets, show_unchanged=show_unchanged)


def format_diff(entries: List[DiffEntry], hide_values: bool = True) -> str:
    """Render diff entries as a human-readable string."""
    if not entries:
        return "No differences found."

    lines: List[str] = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}

    for entry in entries:
        sym = symbols[entry.status]
        if hide_values:
            if entry.status == "changed":
                lines.append(f"{sym} {entry.key}  [value changed]")
            else:
                lines.append(f"{sym} {entry.key}")
        else:
            if entry.status == "added":
                lines.append(f"{sym} {entry.key}={entry.new_value}")
            elif entry.status == "removed":
                lines.append(f"{sym} {entry.key}={entry.old_value}")
            elif entry.status == "changed":
                lines.append(f"{sym} {entry.key}: {entry.old_value!r} -> {entry.new_value!r}")
            else:
                lines.append(f"{sym} {entry.key}={entry.new_value}")

    return "\n".join(lines)
