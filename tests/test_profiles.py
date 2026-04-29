"""Tests for envault/profiles.py."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.profiles import (
    ProfilesError,
    save_profile,
    get_profile,
    list_profiles,
    delete_profile,
    rename_profile,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_save_and_get_profile(vault_path):
    save_profile(vault_path, "production", ["DB_URL", "SECRET_KEY"])
    keys = get_profile(vault_path, "production")
    assert keys == ["DB_URL", "SECRET_KEY"]


def test_get_missing_profile_raises(vault_path):
    with pytest.raises(ProfilesError, match="does not exist"):
        get_profile(vault_path, "nonexistent")


def test_save_empty_name_raises(vault_path):
    with pytest.raises(ProfilesError, match="must not be empty"):
        save_profile(vault_path, "", ["KEY"])


def test_save_empty_keys_raises(vault_path):
    with pytest.raises(ProfilesError, match="at least one key"):
        save_profile(vault_path, "staging", [])


def test_keys_are_sorted_and_deduplicated(vault_path):
    save_profile(vault_path, "dev", ["Z_KEY", "A_KEY", "A_KEY"])
    assert get_profile(vault_path, "dev") == ["A_KEY", "Z_KEY"]


def test_list_profiles_empty(vault_path):
    assert list_profiles(vault_path) == []


def test_list_profiles_sorted(vault_path):
    save_profile(vault_path, "staging", ["K"])
    save_profile(vault_path, "production", ["K"])
    save_profile(vault_path, "dev", ["K"])
    assert list_profiles(vault_path) == ["dev", "production", "staging"]


def test_delete_existing_profile(vault_path):
    save_profile(vault_path, "temp", ["KEY"])
    assert delete_profile(vault_path, "temp") is True
    assert "temp" not in list_profiles(vault_path)


def test_delete_missing_profile_returns_false(vault_path):
    assert delete_profile(vault_path, "ghost") is False


def test_overwrite_profile(vault_path):
    save_profile(vault_path, "prod", ["OLD_KEY"])
    save_profile(vault_path, "prod", ["NEW_KEY"])
    assert get_profile(vault_path, "prod") == ["NEW_KEY"]


def test_rename_profile(vault_path):
    save_profile(vault_path, "old", ["KEY"])
    rename_profile(vault_path, "old", "new")
    assert "new" in list_profiles(vault_path)
    assert "old" not in list_profiles(vault_path)


def test_rename_missing_profile_raises(vault_path):
    with pytest.raises(ProfilesError, match="does not exist"):
        rename_profile(vault_path, "ghost", "new_name")


def test_rename_to_existing_name_raises(vault_path):
    save_profile(vault_path, "a", ["KEY"])
    save_profile(vault_path, "b", ["KEY"])
    with pytest.raises(ProfilesError, match="already exists"):
        rename_profile(vault_path, "a", "b")
