"""Vault locking — prevent concurrent writes to a vault file."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

STALE_LOCK_SECONDS = 30


class LockError(Exception):
    """Raised when a vault lock cannot be acquired or released."""


def _lock_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".lock")


def acquire(vault_path: Path, owner: str = "envault", timeout: float = 5.0) -> None:
    """Acquire an exclusive lock for *vault_path*.

    Polls until *timeout* seconds have elapsed.  Stale locks older than
    ``STALE_LOCK_SECONDS`` are automatically removed before retrying.

    Raises
    ------
    LockError
        If the lock cannot be acquired within *timeout* seconds.
    """
    lock_file = _lock_path(vault_path)
    deadline = time.monotonic() + timeout

    while True:
        if lock_file.exists():
            try:
                data = json.loads(lock_file.read_text())
                age = time.time() - data.get("acquired_at", 0)
                if age > STALE_LOCK_SECONDS:
                    lock_file.unlink(missing_ok=True)
            except (json.JSONDecodeError, OSError):
                lock_file.unlink(missing_ok=True)

        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as fh:
                json.dump({"owner": owner, "acquired_at": time.time(), "pid": os.getpid()}, fh)
            return
        except FileExistsError:
            pass

        if time.monotonic() >= deadline:
            raise LockError(
                f"Could not acquire lock for '{vault_path}' within {timeout}s. "
                f"Lock file: {lock_file}"
            )
        time.sleep(0.05)


def release(vault_path: Path) -> None:
    """Release the lock held for *vault_path*.

    Raises
    ------
    LockError
        If no lock file exists for the given vault.
    """
    lock_file = _lock_path(vault_path)
    if not lock_file.exists():
        raise LockError(f"No lock file found for '{vault_path}'.")
    lock_file.unlink()


def is_locked(vault_path: Path) -> bool:
    """Return ``True`` if a (non-stale) lock exists for *vault_path*."""
    lock_file = _lock_path(vault_path)
    if not lock_file.exists():
        return False
    try:
        data = json.loads(lock_file.read_text())
        age = time.time() - data.get("acquired_at", 0)
        return age <= STALE_LOCK_SECONDS
    except (json.JSONDecodeError, OSError):
        return False


def lock_info(vault_path: Path) -> Optional[dict]:
    """Return the lock metadata dict, or ``None`` if the vault is not locked."""
    if not is_locked(vault_path):
        return None
    try:
        return json.loads(_lock_path(vault_path).read_text())
    except (json.JSONDecodeError, OSError):
        return None
