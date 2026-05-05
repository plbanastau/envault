"""Tests for envault.scoping."""

import pytest

from envault.scoping import (
    ScopingError,
    assign_scope,
    clear_scopes,
    get_scopes,
    keys_in_scope,
    list_scopes,
    remove_scope,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_assign_scope_and_get_scopes(vault_path):
    assign_scope(vault_path, "DB_URL", "prod")
    assert get_scopes(vault_path, "DB_URL") == ["prod"]


def test_assign_multiple_scopes_sorted(vault_path):
    assign_scope(vault_path, "API_KEY", "staging")
    assign_scope(vault_path, "API_KEY", "dev")
    assert get_scopes(vault_path, "API_KEY") == ["dev", "staging"]


def test_assign_duplicate_scope_is_idempotent(vault_path):
    assign_scope(vault_path, "SECRET", "dev")
    assign_scope(vault_path, "SECRET", "dev")
    assert get_scopes(vault_path, "SECRET") == ["dev"]


def test_get_scopes_returns_empty_for_unscoped_key(vault_path):
    assert get_scopes(vault_path, "UNKNOWN") == []


def test_remove_scope_returns_true_when_removed(vault_path):
    assign_scope(vault_path, "TOKEN", "prod")
    result = remove_scope(vault_path, "TOKEN", "prod")
    assert result is True
    assert get_scopes(vault_path, "TOKEN") == []


def test_remove_scope_returns_false_when_not_found(vault_path):
    result = remove_scope(vault_path, "TOKEN", "nonexistent")
    assert result is False


def test_remove_last_scope_cleans_up_key_entry(vault_path):
    assign_scope(vault_path, "ONLY", "dev")
    remove_scope(vault_path, "ONLY", "dev")
    assert "ONLY" not in list_scopes(vault_path)


def test_keys_in_scope_returns_sorted_keys(vault_path):
    assign_scope(vault_path, "Z_KEY", "prod")
    assign_scope(vault_path, "A_KEY", "prod")
    assign_scope(vault_path, "M_KEY", "dev")
    assert keys_in_scope(vault_path, "prod") == ["A_KEY", "Z_KEY"]


def test_keys_in_scope_empty_when_no_match(vault_path):
    assign_scope(vault_path, "DB_URL", "dev")
    assert keys_in_scope(vault_path, "prod") == []


def test_list_scopes_returns_all_unique_scopes(vault_path):
    assign_scope(vault_path, "KEY1", "dev")
    assign_scope(vault_path, "KEY2", "prod")
    assign_scope(vault_path, "KEY3", "dev")
    assert list_scopes(vault_path) == ["dev", "prod"]


def test_list_scopes_empty_before_any_assigned(vault_path):
    assert list_scopes(vault_path) == []


def test_clear_scopes_removes_all_assignments(vault_path):
    assign_scope(vault_path, "KEY", "dev")
    assign_scope(vault_path, "KEY", "prod")
    clear_scopes(vault_path, "KEY")
    assert get_scopes(vault_path, "KEY") == []


def test_assign_scope_empty_key_raises(vault_path):
    with pytest.raises(ScopingError, match="Key must not be empty"):
        assign_scope(vault_path, "", "dev")


def test_assign_scope_empty_scope_raises(vault_path):
    with pytest.raises(ScopingError, match="Scope must not be empty"):
        assign_scope(vault_path, "MY_KEY", "")
