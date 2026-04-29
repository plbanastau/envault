"""Tests for envault.history module."""

import time
import pytest

from envault.history import (
    HistoryError,
    record_change,
    get_history,
    clear_history,
    list_tracked_keys,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_get_history_empty_before_any_record(vault_path):
    assert get_history(vault_path, "MY_KEY") == []


def test_record_change_creates_entry(vault_path):
    record_change(vault_path, "DB_PASS", "supersecret", actor="alice")
    history = get_history(vault_path, "DB_PASS")
    assert len(history) == 1
    assert history[0]["actor"] == "alice"


def test_record_change_value_preview_masked(vault_path):
    record_change(vault_path, "API_KEY", "abcdefgh")
    entry = get_history(vault_path, "API_KEY")[0]
    assert entry["value_preview"].endswith("****")
    assert "abcd" in entry["value_preview"]


def test_record_change_short_value_fully_masked(vault_path):
    record_change(vault_path, "PIN", "42")
    entry = get_history(vault_path, "PIN")[0]
    assert entry["value_preview"] == "****"


def test_record_multiple_changes_ordered(vault_path):
    record_change(vault_path, "TOKEN", "first_value")
    time.sleep(0.01)
    record_change(vault_path, "TOKEN", "second_value")
    history = get_history(vault_path, "TOKEN")
    assert len(history) == 2
    assert history[0]["timestamp"] < history[1]["timestamp"]


def test_record_change_empty_key_raises(vault_path):
    with pytest.raises(HistoryError):
        record_change(vault_path, "", "value")


def test_get_history_empty_key_raises(vault_path):
    with pytest.raises(HistoryError):
        get_history(vault_path, "")


def test_list_tracked_keys_sorted(vault_path):
    record_change(vault_path, "ZEBRA", "z")
    record_change(vault_path, "ALPHA", "a")
    record_change(vault_path, "MIDDLE", "m")
    keys = list_tracked_keys(vault_path)
    assert keys == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_clear_history_specific_key(vault_path):
    record_change(vault_path, "KEY_A", "val")
    record_change(vault_path, "KEY_B", "val")
    clear_history(vault_path, "KEY_A")
    assert get_history(vault_path, "KEY_A") == []
    assert len(get_history(vault_path, "KEY_B")) == 1


def test_clear_history_all_keys(vault_path):
    record_change(vault_path, "KEY_A", "val")
    record_change(vault_path, "KEY_B", "val")
    clear_history(vault_path)
    assert list_tracked_keys(vault_path) == []


def test_record_change_has_timestamp(vault_path):
    before = time.time()
    record_change(vault_path, "TS_KEY", "some_value")
    after = time.time()
    entry = get_history(vault_path, "TS_KEY")[0]
    assert before <= entry["timestamp"] <= after
