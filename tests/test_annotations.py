"""Tests for envault.annotations."""

import pytest

from envault.annotations import (
    AnnotationError,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_and_get_annotation(vault_path):
    set_annotation(vault_path, "DB_URL", "Primary database connection string")
    assert get_annotation(vault_path, "DB_URL") == "Primary database connection string"


def test_get_annotation_returns_none_for_unknown_key(vault_path):
    assert get_annotation(vault_path, "MISSING") is None


def test_set_annotation_overwrites_existing(vault_path):
    set_annotation(vault_path, "API_KEY", "old note")
    set_annotation(vault_path, "API_KEY", "new note")
    assert get_annotation(vault_path, "API_KEY") == "new note"


def test_set_annotation_empty_key_raises(vault_path):
    with pytest.raises(AnnotationError, match="key"):
        set_annotation(vault_path, "", "some note")


def test_set_annotation_empty_note_raises(vault_path):
    with pytest.raises(AnnotationError, match="note"):
        set_annotation(vault_path, "DB_URL", "")


def test_remove_existing_annotation_returns_true(vault_path):
    set_annotation(vault_path, "SECRET", "a note")
    assert remove_annotation(vault_path, "SECRET") is True
    assert get_annotation(vault_path, "SECRET") is None


def test_remove_missing_annotation_returns_false(vault_path):
    assert remove_annotation(vault_path, "GHOST") is False


def test_list_annotations_empty_before_any_set(vault_path):
    assert list_annotations(vault_path) == {}


def test_list_annotations_sorted(vault_path):
    set_annotation(vault_path, "Z_KEY", "last")
    set_annotation(vault_path, "A_KEY", "first")
    set_annotation(vault_path, "M_KEY", "middle")
    keys = list(list_annotations(vault_path).keys())
    assert keys == ["A_KEY", "M_KEY", "Z_KEY"]


def test_list_annotations_returns_all_entries(vault_path):
    set_annotation(vault_path, "FOO", "foo note")
    set_annotation(vault_path, "BAR", "bar note")
    result = list_annotations(vault_path)
    assert result["FOO"] == "foo note"
    assert result["BAR"] == "bar note"


def test_annotations_persisted_across_calls(vault_path):
    set_annotation(vault_path, "PERSIST", "persisted note")
    # Simulate a fresh call by re-importing / calling get again
    assert get_annotation(vault_path, "PERSIST") == "persisted note"
