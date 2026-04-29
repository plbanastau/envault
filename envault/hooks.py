"""Lifecycle hooks for envault vault operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

HOOK_EVENTS = ("pre_set", "post_set", "pre_delete", "post_delete", "post_rotate")


class HooksError(Exception):
    pass


def _hooks_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".hooks.json")


def _load(vault_path: Path) -> Dict[str, List[str]]:
    p = _hooks_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _hooks_path(vault_path).write_text(json.dumps(data, indent=2))


def register_hook(vault_path: Path, event: str, command: str) -> None:
    """Register a shell command to run on a given lifecycle event."""
    if event not in HOOK_EVENTS:
        raise HooksError(f"Unknown event '{event}'. Valid events: {HOOK_EVENTS}")
    if not command.strip():
        raise HooksError("Hook command must not be empty.")
    data = _load(vault_path)
    data.setdefault(event, [])
    if command not in data[event]:
        data[event].append(command)
    _save(vault_path, data)


def unregister_hook(vault_path: Path, event: str, command: str) -> bool:
    """Remove a hook command. Returns True if removed, False if not found."""
    data = _load(vault_path)
    hooks = data.get(event, [])
    if command not in hooks:
        return False
    hooks.remove(command)
    data[event] = hooks
    _save(vault_path, data)
    return True


def list_hooks(vault_path: Path, event: Optional[str] = None) -> Dict[str, List[str]]:
    """Return all hooks, optionally filtered by event."""
    data = _load(vault_path)
    if event is not None:
        return {event: data.get(event, [])}
    return {e: data.get(e, []) for e in HOOK_EVENTS}


def fire(vault_path: Path, event: str, env: Optional[Dict[str, str]] = None) -> List[str]:
    """Execute all hooks for the given event. Returns list of executed commands."""
    import subprocess
    import os

    if event not in HOOK_EVENTS:
        raise HooksError(f"Unknown event '{event}'.")

    data = _load(vault_path)
    commands = data.get(event, [])
    run_env = {**os.environ, **(env or {})}

    for cmd in commands:
        result = subprocess.run(cmd, shell=True, env=run_env)
        if result.returncode != 0:
            raise HooksError(f"Hook command failed (exit {result.returncode}): {cmd}")

    return commands
