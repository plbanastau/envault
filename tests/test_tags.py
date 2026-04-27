"""Tests for envault.tags module."""

import pytest

from envault.vault import Vault
from envault.tags import (
    add_tag,
    remove_tag,
    get_tags,
    keys_for_tag,
    all_tags,
    TagsError,
    TAGS_META_KEY,
)

PASSWORD = "test-secret"


@pytest.fixture()
def tmp_vault(tmp_path):
    path = tmp_path / "vault.json"
    v = Vault(str(path), PASSWORD)
    v.set("DB_URL", "postgres://localhost/db", PASSWORD)
    v.set("API_KEY", "abc123", PASSWORD)
    v.set("REDIS_URL", "redis://localhost", PASSWORD)
    return v


def test_add_tag_and_get_tags(tmp_vault):
    add_tag(tmp_vault, "DB_URL", "db", PASSWORD)
    assert get_tags(tmp_vault, "DB_URL") == ["db"]


def test_add_multiple_tags_sorted(tmp_vault):
    add_tag(tmp_vault, "DB_URL", "prod", PASSWORD)
    add_tag(tmp_vault, "DB_URL", "db", PASSWORD)
    assert get_tags(tmp_vault, "DB_URL") == ["db", "prod"]


def test_add_duplicate_tag_is_idempotent(tmp_vault):
    add_tag(tmp_vault, "API_KEY", "ci", PASSWORD)
    add_tag(tmp_vault, "API_KEY", "ci", PASSWORD)
    assert get_tags(tmp_vault, "API_KEY") == ["ci"]


def test_get_tags_returns_empty_for_untagged_key(tmp_vault):
    assert get_tags(tmp_vault, "REDIS_URL") == []


def test_remove_tag_returns_true(tmp_vault):
    add_tag(tmp_vault, "API_KEY", "ci", PASSWORD)
    result = remove_tag(tmp_vault, "API_KEY", "ci", PASSWORD)
    assert result is True
    assert get_tags(tmp_vault, "API_KEY") == []


def test_remove_tag_returns_false_when_not_present(tmp_vault):
    result = remove_tag(tmp_vault, "API_KEY", "nonexistent", PASSWORD)
    assert result is False


def test_keys_for_tag(tmp_vault):
    add_tag(tmp_vault, "DB_URL", "db", PASSWORD)
    add_tag(tmp_vault, "REDIS_URL", "db", PASSWORD)
    add_tag(tmp_vault, "API_KEY", "ci", PASSWORD)
    assert keys_for_tag(tmp_vault, "db") == ["DB_URL", "REDIS_URL"]


def test_keys_for_tag_empty_when_no_match(tmp_vault):
    assert keys_for_tag(tmp_vault, "ghost") == []


def test_all_tags(tmp_vault):
    add_tag(tmp_vault, "DB_URL", "db", PASSWORD)
    add_tag(tmp_vault, "API_KEY", "ci", PASSWORD)
    add_tag(tmp_vault, "REDIS_URL", "db", PASSWORD)
    assert all_tags(tmp_vault) == ["ci", "db"]


def test_all_tags_empty_vault(tmp_vault):
    assert all_tags(tmp_vault) == []


def test_add_tag_raises_on_empty_key(tmp_vault):
    with pytest.raises(TagsError):
        add_tag(tmp_vault, "", "db", PASSWORD)


def test_add_tag_raises_on_reserved_meta_key(tmp_vault):
    with pytest.raises(TagsError):
        add_tag(tmp_vault, TAGS_META_KEY, "db", PASSWORD)
