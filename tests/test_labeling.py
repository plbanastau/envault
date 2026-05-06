"""Tests for envault.labeling."""

import pytest

from envault.labeling import (
    LabelingError,
    get_label,
    keys_with_label,
    list_labels,
    remove_label,
    set_label,
)


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_and_get_label(vault_path):
    set_label(vault_path, "DB_PASSWORD", "Database Password")
    assert get_label(vault_path, "DB_PASSWORD") == "Database Password"


def test_get_label_returns_none_for_unlabeled_key(vault_path):
    assert get_label(vault_path, "UNKNOWN_KEY") is None


def test_set_label_empty_key_raises(vault_path):
    with pytest.raises(LabelingError, match="key"):
        set_label(vault_path, "", "Some Label")


def test_set_label_empty_label_raises(vault_path):
    with pytest.raises(LabelingError, match="label"):
        set_label(vault_path, "MY_KEY", "")


def test_set_label_overwrites_existing(vault_path):
    set_label(vault_path, "API_KEY", "Old Label")
    set_label(vault_path, "API_KEY", "New Label")
    assert get_label(vault_path, "API_KEY") == "New Label"


def test_remove_label_returns_true(vault_path):
    set_label(vault_path, "TOKEN", "Auth Token")
    assert remove_label(vault_path, "TOKEN") is True
    assert get_label(vault_path, "TOKEN") is None


def test_remove_label_returns_false_when_not_set(vault_path):
    assert remove_label(vault_path, "NONEXISTENT") is False


def test_list_labels_empty(vault_path):
    assert list_labels(vault_path) == []


def test_list_labels_sorted_by_key(vault_path):
    set_label(vault_path, "Z_KEY", "Zulu")
    set_label(vault_path, "A_KEY", "Alpha")
    set_label(vault_path, "M_KEY", "Mike")
    result = list_labels(vault_path)
    assert [e["key"] for e in result] == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_labels_contains_correct_entries(vault_path):
    set_label(vault_path, "DB_HOST", "Database Host")
    entries = list_labels(vault_path)
    assert entries[0] == {"key": "DB_HOST", "label": "Database Host"}


def test_keys_with_label_returns_matching_keys(vault_path):
    set_label(vault_path, "DB_PASS", "Sensitive")
    set_label(vault_path, "API_SECRET", "Sensitive")
    set_label(vault_path, "APP_NAME", "Config")
    result = keys_with_label(vault_path, "Sensitive")
    assert result == ["API_SECRET", "DB_PASS"]


def test_keys_with_label_no_match_returns_empty(vault_path):
    set_label(vault_path, "MY_KEY", "Other")
    assert keys_with_label(vault_path, "Sensitive") == []
