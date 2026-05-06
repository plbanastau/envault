"""Tests for envault.grouping."""

import pytest
from pathlib import Path

from envault.grouping import (
    GroupingError,
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    delete_group,
    groups_for_key,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    vp = tmp_path / "test.vault"
    vp.touch()
    return vp


def test_add_to_group_and_get_group(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    assert get_group(vault_path, "infra") == ["DB_HOST"]


def test_add_multiple_keys_sorted(vault_path):
    add_to_group(vault_path, "infra", "DB_PORT")
    add_to_group(vault_path, "infra", "DB_HOST")
    assert get_group(vault_path, "infra") == ["DB_HOST", "DB_PORT"]


def test_add_duplicate_key_is_idempotent(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    add_to_group(vault_path, "infra", "DB_HOST")
    assert get_group(vault_path, "infra") == ["DB_HOST"]


def test_get_group_returns_empty_for_unknown_group(vault_path):
    assert get_group(vault_path, "nonexistent") == []


def test_list_groups_empty(vault_path):
    assert list_groups(vault_path) == []


def test_list_groups_sorted(vault_path):
    add_to_group(vault_path, "web", "PORT")
    add_to_group(vault_path, "infra", "DB_HOST")
    assert list_groups(vault_path) == ["infra", "web"]


def test_remove_from_group_returns_true(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    result = remove_from_group(vault_path, "infra", "DB_HOST")
    assert result is True
    assert get_group(vault_path, "infra") == []


def test_remove_from_group_missing_key_returns_false(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    result = remove_from_group(vault_path, "infra", "MISSING")
    assert result is False


def test_remove_last_key_removes_group(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    remove_from_group(vault_path, "infra", "DB_HOST")
    assert "infra" not in list_groups(vault_path)


def test_delete_group_returns_true(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    result = delete_group(vault_path, "infra")
    assert result is True
    assert list_groups(vault_path) == []


def test_delete_group_missing_returns_false(vault_path):
    assert delete_group(vault_path, "ghost") is False


def test_groups_for_key_returns_all_groups(vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    add_to_group(vault_path, "web", "DB_HOST")
    add_to_group(vault_path, "cache", "REDIS_URL")
    assert groups_for_key(vault_path, "DB_HOST") == ["infra", "web"]


def test_groups_for_key_returns_empty_when_not_in_any_group(vault_path):
    assert groups_for_key(vault_path, "ORPHAN_KEY") == []


def test_add_empty_group_name_raises(vault_path):
    with pytest.raises(GroupingError, match="Group name"):
        add_to_group(vault_path, "", "DB_HOST")


def test_add_empty_key_raises(vault_path):
    with pytest.raises(GroupingError, match="Key"):
        add_to_group(vault_path, "infra", "")
