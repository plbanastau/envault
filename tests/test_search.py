"""Tests for envault.search module."""

import pytest

from envault.vault import Vault
from envault.search import search, search_by_glob, search_by_regex, SearchError


PASSWORD = "hunter2"


@pytest.fixture
def populated_vault(tmp_path):
    vault_path = tmp_path / "vault.json"
    v = Vault(str(vault_path))
    secrets = {
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "DATABASE_URL": "postgres://localhost/db",
        "REDIS_URL": "redis://localhost",
        "APP_SECRET": "topsecret",
    }
    for k, val in secrets.items():
        v.set(k, val, PASSWORD)
    return v


def test_glob_prefix_match(populated_vault):
    results = search_by_glob(populated_vault, PASSWORD, "AWS_*")
    keys = [r.key for r in results]
    assert "AWS_ACCESS_KEY_ID" in keys
    assert "AWS_SECRET_ACCESS_KEY" in keys
    assert "DATABASE_URL" not in keys


def test_glob_suffix_match(populated_vault):
    results = search_by_glob(populated_vault, PASSWORD, "*_URL")
    keys = [r.key for r in results]
    assert "DATABASE_URL" in keys
    assert "REDIS_URL" in keys
    assert "APP_SECRET" not in keys


def test_glob_no_match_returns_empty(populated_vault):
    results = search_by_glob(populated_vault, PASSWORD, "NONEXISTENT_*")
    assert results == []


def test_glob_results_sorted(populated_vault):
    results = search_by_glob(populated_vault, PASSWORD, "*")
    keys = [r.key for r in results]
    assert keys == sorted(keys)


def test_glob_matched_by_field(populated_vault):
    results = search_by_glob(populated_vault, PASSWORD, "APP_*")
    assert all(r.matched_by == "key_glob" for r in results)


def test_regex_match(populated_vault):
    results = search_by_regex(populated_vault, PASSWORD, r"^AWS_")
    keys = [r.key for r in results]
    assert "AWS_ACCESS_KEY_ID" in keys
    assert "AWS_SECRET_ACCESS_KEY" in keys


def test_regex_case_sensitive(populated_vault):
    results = search_by_regex(populated_vault, PASSWORD, r"aws_")
    assert results == []


def test_regex_matched_by_field(populated_vault):
    results = search_by_regex(populated_vault, PASSWORD, r"URL$")
    assert all(r.matched_by == "key_regex" for r in results)


def test_invalid_regex_raises(populated_vault):
    with pytest.raises(SearchError, match="Invalid regex"):
        search_by_regex(populated_vault, PASSWORD, r"[unclosed")


def test_search_delegates_to_glob_by_default(populated_vault):
    results = search(populated_vault, PASSWORD, "AWS_*")
    assert len(results) == 2


def test_search_delegates_to_regex_when_flag_set(populated_vault):
    results = search(populated_vault, PASSWORD, r"SECRET", use_regex=True)
    keys = [r.key for r in results]
    assert "AWS_SECRET_ACCESS_KEY" in keys
    assert "APP_SECRET" in keys
