"""Tests for envault.deprecation module."""

import pytest

from envault.deprecation import (
    DeprecationError,
    get_deprecation,
    is_deprecated,
    list_deprecated,
    mark_deprecated,
    unmark_deprecated,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_mark_deprecated_returns_entry(vault_path):
    entry = mark_deprecated(vault_path, "OLD_API_KEY", "Use NEW_API_KEY instead", replacement="NEW_API_KEY")
    assert entry["reason"] == "Use NEW_API_KEY instead"
    assert entry["replacement"] == "NEW_API_KEY"


def test_mark_deprecated_no_replacement(vault_path):
    entry = mark_deprecated(vault_path, "LEGACY_TOKEN", "No longer supported")
    assert entry["replacement"] is None


def test_is_deprecated_true_after_mark(vault_path):
    mark_deprecated(vault_path, "OLD_KEY", "Deprecated")
    assert is_deprecated(vault_path, "OLD_KEY") is True


def test_is_deprecated_false_for_unmarked_key(vault_path):
    assert is_deprecated(vault_path, "ACTIVE_KEY") is False


def test_get_deprecation_returns_entry(vault_path):
    mark_deprecated(vault_path, "OLD_KEY", "Old reason", replacement="NEW_KEY")
    result = get_deprecation(vault_path, "OLD_KEY")
    assert result is not None
    assert result["reason"] == "Old reason"
    assert result["replacement"] == "NEW_KEY"


def test_get_deprecation_returns_none_for_unknown(vault_path):
    assert get_deprecation(vault_path, "MISSING_KEY") is None


def test_unmark_deprecated_removes_entry(vault_path):
    mark_deprecated(vault_path, "OLD_KEY", "Reason")
    result = unmark_deprecated(vault_path, "OLD_KEY")
    assert result is True
    assert is_deprecated(vault_path, "OLD_KEY") is False


def test_unmark_deprecated_missing_key_returns_false(vault_path):
    assert unmark_deprecated(vault_path, "NONEXISTENT") is False


def test_list_deprecated_sorted(vault_path):
    mark_deprecated(vault_path, "Z_KEY", "Last")
    mark_deprecated(vault_path, "A_KEY", "First")
    mark_deprecated(vault_path, "M_KEY", "Middle")
    entries = list_deprecated(vault_path)
    keys = [e["key"] for e in entries]
    assert keys == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_deprecated_empty_before_any_marked(vault_path):
    assert list_deprecated(vault_path) == []


def test_mark_deprecated_empty_key_raises(vault_path):
    with pytest.raises(DeprecationError, match="key"):
        mark_deprecated(vault_path, "", "Some reason")


def test_mark_deprecated_empty_reason_raises(vault_path):
    with pytest.raises(DeprecationError, match="reason"):
        mark_deprecated(vault_path, "OLD_KEY", "")


def test_mark_deprecated_overwrites_existing(vault_path):
    mark_deprecated(vault_path, "OLD_KEY", "First reason")
    mark_deprecated(vault_path, "OLD_KEY", "Updated reason", replacement="NEW")
    entry = get_deprecation(vault_path, "OLD_KEY")
    assert entry["reason"] == "Updated reason"
    assert entry["replacement"] == "NEW"
