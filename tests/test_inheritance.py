"""Tests for envault.inheritance."""

import pytest
from pathlib import Path

from envault.inheritance import (
    InheritanceError,
    set_parent,
    get_parent,
    clear_parent,
    add_override,
    remove_override,
    list_overrides,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    vp = tmp_path / "child.vault"
    vp.write_text("{}")
    return vp


@pytest.fixture()
def parent_path(tmp_path: Path) -> Path:
    pp = tmp_path / "parent.vault"
    pp.write_text("{}")
    return pp


def test_get_parent_returns_none_when_not_set(vault_path):
    assert get_parent(vault_path) is None


def test_set_parent_and_get_parent(vault_path, parent_path):
    set_parent(vault_path, parent_path)
    result = get_parent(vault_path)
    assert result == parent_path.resolve()


def test_set_parent_self_raises(vault_path):
    with pytest.raises(InheritanceError, match="itself"):
        set_parent(vault_path, vault_path)


def test_clear_parent_returns_true_when_parent_existed(vault_path, parent_path):
    set_parent(vault_path, parent_path)
    assert clear_parent(vault_path) is True


def test_clear_parent_returns_false_when_no_parent(vault_path):
    assert clear_parent(vault_path) is False


def test_clear_parent_removes_parent(vault_path, parent_path):
    set_parent(vault_path, parent_path)
    clear_parent(vault_path)
    assert get_parent(vault_path) is None


def test_add_override_and_list(vault_path):
    add_override(vault_path, "DB_PASSWORD")
    assert "DB_PASSWORD" in list_overrides(vault_path)


def test_add_override_empty_key_raises(vault_path):
    with pytest.raises(InheritanceError):
        add_override(vault_path, "")


def test_add_duplicate_override_is_idempotent(vault_path):
    add_override(vault_path, "API_KEY")
    add_override(vault_path, "API_KEY")
    assert list_overrides(vault_path).count("API_KEY") == 1


def test_overrides_are_sorted(vault_path):
    add_override(vault_path, "Z_KEY")
    add_override(vault_path, "A_KEY")
    overrides = list_overrides(vault_path)
    assert overrides == sorted(overrides)


def test_remove_override_returns_true_when_present(vault_path):
    add_override(vault_path, "SECRET")
    assert remove_override(vault_path, "SECRET") is True


def test_remove_override_returns_false_when_absent(vault_path):
    assert remove_override(vault_path, "MISSING") is False


def test_remove_override_actually_removes_key(vault_path):
    add_override(vault_path, "TOKEN")
    remove_override(vault_path, "TOKEN")
    assert "TOKEN" not in list_overrides(vault_path)


def test_list_overrides_empty_by_default(vault_path):
    assert list_overrides(vault_path) == []
