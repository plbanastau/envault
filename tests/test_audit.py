"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path

from envault.audit import record, get_log, clear_log, _audit_path


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_record_creates_audit_file(vault_path):
    record(vault_path, "set", "DB_URL")
    audit_file = _audit_path(vault_path)
    assert audit_file.exists()


def test_record_entry_has_required_fields(vault_path):
    record(vault_path, "set", "API_KEY")
    entries = get_log(vault_path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["action"] == "set"
    assert entry["key"] == "API_KEY"
    assert "timestamp" in entry
    assert "actor" in entry


def test_record_multiple_entries(vault_path):
    record(vault_path, "set", "KEY_A")
    record(vault_path, "get", "KEY_A")
    record(vault_path, "delete", "KEY_A")
    entries = get_log(vault_path)
    assert len(entries) == 3
    assert [e["action"] for e in entries] == ["set", "get", "delete"]


def test_record_custom_actor(vault_path):
    record(vault_path, "set", "SECRET", actor="ci-bot")
    entries = get_log(vault_path)
    assert entries[0]["actor"] == "ci-bot"


def test_get_log_empty_when_no_file(vault_path):
    entries = get_log(vault_path)
    assert entries == []


def test_clear_log_removes_file(vault_path):
    record(vault_path, "set", "X")
    clear_log(vault_path)
    assert not _audit_path(vault_path).exists()


def test_clear_log_no_error_if_missing(vault_path):
    # Should not raise even if file doesn't exist
    clear_log(vault_path)


def test_get_log_returns_empty_on_corrupted_file(vault_path):
    audit_file = _audit_path(vault_path)
    audit_file.write_text("not valid json{{{")
    entries = get_log(vault_path)
    assert entries == []
