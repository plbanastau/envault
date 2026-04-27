"""Tests for envault.diff module."""

import pytest

from envault.diff import DiffEntry, diff_dicts, format_diff


# ---------------------------------------------------------------------------
# diff_dicts
# ---------------------------------------------------------------------------

def test_added_key_detected():
    entries = diff_dicts(old={}, new={"NEW_KEY": "value"})
    assert len(entries) == 1
    assert entries[0].status == "added"
    assert entries[0].key == "NEW_KEY"
    assert entries[0].new_value == "value"
    assert entries[0].old_value is None


def test_removed_key_detected():
    entries = diff_dicts(old={"OLD_KEY": "v"}, new={})
    assert len(entries) == 1
    assert entries[0].status == "removed"
    assert entries[0].key == "OLD_KEY"
    assert entries[0].old_value == "v"


def test_changed_key_detected():
    entries = diff_dicts(old={"K": "old"}, new={"K": "new"})
    assert len(entries) == 1
    assert entries[0].status == "changed"
    assert entries[0].old_value == "old"
    assert entries[0].new_value == "new"


def test_unchanged_key_excluded_by_default():
    entries = diff_dicts(old={"K": "same"}, new={"K": "same"})
    assert entries == []


def test_unchanged_key_included_when_requested():
    entries = diff_dicts(old={"K": "same"}, new={"K": "same"}, show_unchanged=True)
    assert len(entries) == 1
    assert entries[0].status == "unchanged"


def test_results_sorted_by_key():
    old = {"Z": "1", "A": "1"}
    new = {"Z": "2", "A": "1", "M": "3"}
    entries = diff_dicts(old, new)
    keys = [e.key for e in entries]
    assert keys == sorted(keys)


def test_mixed_diff():
    old = {"A": "1", "B": "old", "C": "3"}
    new = {"B": "new", "C": "3", "D": "4"}
    entries = diff_dicts(old, new)
    statuses = {e.key: e.status for e in entries}
    assert statuses["A"] == "removed"
    assert statuses["B"] == "changed"
    assert statuses["D"] == "added"
    assert "C" not in statuses  # unchanged, excluded by default


# ---------------------------------------------------------------------------
# format_diff
# ---------------------------------------------------------------------------

def test_format_diff_no_entries_returns_message():
    result = format_diff([])
    assert "No differences" in result


def test_format_diff_hides_values_by_default():
    entries = [DiffEntry(key="SECRET", status="changed", old_value="a", new_value="b")]
    result = format_diff(entries, hide_values=True)
    assert "a" not in result
    assert "b" not in result
    assert "[value changed]" in result


def test_format_diff_shows_values_when_requested():
    entries = [DiffEntry(key="K", status="added", new_value="hello")]
    result = format_diff(entries, hide_values=False)
    assert "hello" in result
    assert "+" in result


def test_format_diff_removed_symbol():
    entries = [DiffEntry(key="K", status="removed", old_value="v")]
    result = format_diff(entries, hide_values=False)
    assert result.startswith("-")
