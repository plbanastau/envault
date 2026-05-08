"""Tests for envault.dependencies."""

import pytest

from envault.dependencies import (
    DependencyError,
    add_dependency,
    get_dependencies,
    get_dependents,
    list_all,
    remove_dependency,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_get_dependencies_empty_before_any_added(vault_path):
    assert get_dependencies(vault_path, "APP_URL") == []


def test_add_dependency_and_get(vault_path):
    add_dependency(vault_path, "DATABASE_URL", "DB_PASSWORD")
    assert get_dependencies(vault_path, "DATABASE_URL") == ["DB_PASSWORD"]


def test_add_multiple_dependencies_sorted(vault_path):
    add_dependency(vault_path, "APP_URL", "PORT")
    add_dependency(vault_path, "APP_URL", "HOST")
    assert get_dependencies(vault_path, "APP_URL") == ["HOST", "PORT"]


def test_add_duplicate_dependency_is_idempotent(vault_path):
    add_dependency(vault_path, "APP_URL", "HOST")
    add_dependency(vault_path, "APP_URL", "HOST")
    assert get_dependencies(vault_path, "APP_URL") == ["HOST"]


def test_add_dependency_self_raises(vault_path):
    with pytest.raises(DependencyError, match="cannot depend on itself"):
        add_dependency(vault_path, "KEY", "KEY")


def test_add_dependency_empty_key_raises(vault_path):
    with pytest.raises(DependencyError, match="key must not be empty"):
        add_dependency(vault_path, "", "OTHER")


def test_add_dependency_empty_depends_on_raises(vault_path):
    with pytest.raises(DependencyError, match="depends_on must not be empty"):
        add_dependency(vault_path, "KEY", "")


def test_remove_existing_dependency_returns_true(vault_path):
    add_dependency(vault_path, "APP", "SECRET")
    result = remove_dependency(vault_path, "APP", "SECRET")
    assert result is True
    assert get_dependencies(vault_path, "APP") == []


def test_remove_nonexistent_dependency_returns_false(vault_path):
    result = remove_dependency(vault_path, "APP", "MISSING")
    assert result is False


def test_remove_last_dependency_cleans_up_key(vault_path):
    add_dependency(vault_path, "APP", "SECRET")
    remove_dependency(vault_path, "APP", "SECRET")
    assert "APP" not in list_all(vault_path)


def test_get_dependents_returns_keys_that_depend_on_target(vault_path):
    add_dependency(vault_path, "SERVICE_A", "SHARED_SECRET")
    add_dependency(vault_path, "SERVICE_B", "SHARED_SECRET")
    dependents = get_dependents(vault_path, "SHARED_SECRET")
    assert dependents == ["SERVICE_A", "SERVICE_B"]


def test_get_dependents_empty_when_nothing_depends(vault_path):
    add_dependency(vault_path, "APP", "DB_PASS")
    assert get_dependents(vault_path, "APP") == []


def test_list_all_returns_full_map(vault_path):
    add_dependency(vault_path, "A", "B")
    add_dependency(vault_path, "A", "C")
    add_dependency(vault_path, "X", "Y")
    result = list_all(vault_path)
    assert result == {"A": ["B", "C"], "X": ["Y"]}
