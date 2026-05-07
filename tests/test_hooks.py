"""Tests for envault.hooks lifecycle hook system."""

import pytest
from pathlib import Path

from envault.hooks import (
    register_hook,
    unregister_hook,
    list_hooks,
    fire,
    HooksError,
    HOOK_EVENTS,
)


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return p


def test_register_hook_stores_command(vault_path):
    register_hook(vault_path, "post_set", "echo hello")
    hooks = list_hooks(vault_path, "post_set")
    assert "echo hello" in hooks["post_set"]


def test_register_hook_invalid_event_raises(vault_path):
    with pytest.raises(HooksError, match="Unknown event"):
        register_hook(vault_path, "on_magic", "echo x")


def test_register_hook_empty_command_raises(vault_path):
    with pytest.raises(HooksError, match="must not be empty"):
        register_hook(vault_path, "post_set", "   ")


def test_register_hook_is_idempotent(vault_path):
    register_hook(vault_path, "pre_set", "echo dup")
    register_hook(vault_path, "pre_set", "echo dup")
    hooks = list_hooks(vault_path, "pre_set")
    assert hooks["pre_set"].count("echo dup") == 1


def test_register_multiple_hooks_for_same_event(vault_path):
    register_hook(vault_path, "post_delete", "echo a")
    register_hook(vault_path, "post_delete", "echo b")
    hooks = list_hooks(vault_path, "post_delete")
    assert len(hooks["post_delete"]) == 2


def test_unregister_existing_hook_returns_true(vault_path):
    register_hook(vault_path, "post_set", "echo remove_me")
    result = unregister_hook(vault_path, "post_set", "echo remove_me")
    assert result is True
    hooks = list_hooks(vault_path, "post_set")
    assert "echo remove_me" not in hooks["post_set"]


def test_unregister_missing_hook_returns_false(vault_path):
    result = unregister_hook(vault_path, "post_set", "echo ghost")
    assert result is False


def test_unregister_invalid_event_raises(vault_path):
    """Unregistering from an unknown event should raise HooksError."""
    with pytest.raises(HooksError, match="Unknown event"):
        unregister_hook(vault_path, "on_magic", "echo x")


def test_list_hooks_all_events_returned(vault_path):
    hooks = list_hooks(vault_path)
    assert set(hooks.keys()) == set(HOOK_EVENTS)


def test_list_hooks_filtered_by_event(vault_path):
    register_hook(vault_path, "post_rotate", "echo rotated")
    hooks = list_hooks(vault_path, "post_rotate")
    assert list(hooks.keys()) == ["post_rotate"]


def test_fire_executes_hook(vault_path):
    register_hook(vault_path, "post_set", "true")
    executed = fire(vault_path, "post_set")
    assert "true" in executed


def test_fire_failing_hook_raises(vault_path):
    register_hook(vault_path, "post_set", "false")
    with pytest.raises(HooksError, match="Hook command failed"):
        fire(vault_path, "post_set")


def test_fire_no_hooks_returns_empty(vault_path):
    executed = fire(vault_path, "pre_delete")
    assert executed == []


def test_fire_invalid_event_raises(vault_path):
    with pytest.raises(HooksError, match="Unknown event"):
        fire(vault_path, "on_something")
