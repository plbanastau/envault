"""Access control: per-key read/write permissions stored alongside the vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set

ACCESS_FILENAME = ".envault_access.json"

ACCESS_READ = "read"
ACCESS_WRITE = "write"
VALID_PERMISSIONS = {ACCESS_READ, ACCESS_WRITE}


class AccessError(Exception):
    """Raised on access-control violations or bad input."""


def _access_path(vault_path: str | Path) -> Path:
    return Path(vault_path).parent / ACCESS_FILENAME


def _load(vault_path: str | Path) -> Dict[str, Dict[str, List[str]]]:
    """Return raw ACL dict: {key: {permission: [actor, ...]}}"""
    p = _access_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str | Path, acl: Dict[str, Dict[str, List[str]]]) -> None:
    p = _access_path(vault_path)
    p.write_text(json.dumps(acl, indent=2, sort_keys=True))


def grant(vault_path: str | Path, key: str, actor: str, permission: str) -> None:
    """Grant *actor* the given *permission* on *key*."""
    if permission not in VALID_PERMISSIONS:
        raise AccessError(f"Unknown permission '{permission}'. Choose from {VALID_PERMISSIONS}.")
    acl = _load(vault_path)
    acl.setdefault(key, {}).setdefault(permission, [])
    actors: List[str] = acl[key][permission]
    if actor not in actors:
        actors.append(actor)
        actors.sort()
    _save(vault_path, acl)


def revoke(vault_path: str | Path, key: str, actor: str, permission: str) -> bool:
    """Revoke *actor*'s *permission* on *key*. Returns True if anything changed."""
    acl = _load(vault_path)
    actors: List[str] = acl.get(key, {}).get(permission, [])
    if actor not in actors:
        return False
    actors.remove(actor)
    _save(vault_path, acl)
    return True


def get_permissions(vault_path: str | Path, key: str, actor: str) -> Set[str]:
    """Return the set of permissions *actor* holds on *key*."""
    acl = _load(vault_path)
    key_acl = acl.get(key, {})
    return {perm for perm in VALID_PERMISSIONS if actor in key_acl.get(perm, [])}


def list_acl(vault_path: str | Path, key: str) -> Dict[str, List[str]]:
    """Return the full ACL for *key* (empty dict if none set)."""
    return _load(vault_path).get(key, {})
