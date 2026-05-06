"""Tests for envault.ranking."""

from __future__ import annotations

import pytest

from envault.ranking import (
    RankingError,
    get_score,
    ranked_keys,
    record_access,
    reset_score,
)


@pytest.fixture()
def vault_path(tmp_path) -> str:
    return str(tmp_path / "vault.json")


def test_record_access_returns_incremented_count(vault_path):
    count = record_access(vault_path, "DB_PASSWORD")
    assert count == 1


def test_record_access_increments_on_repeated_calls(vault_path):
    record_access(vault_path, "API_KEY")
    record_access(vault_path, "API_KEY")
    count = record_access(vault_path, "API_KEY")
    assert count == 3


def test_get_score_returns_zero_for_unknown_key(vault_path):
    assert get_score(vault_path, "UNKNOWN") == 0


def test_get_score_reflects_recorded_accesses(vault_path):
    record_access(vault_path, "SECRET")
    record_access(vault_path, "SECRET")
    assert get_score(vault_path, "SECRET") == 2


def test_ranked_keys_empty_before_any_access(vault_path):
    assert ranked_keys(vault_path) == []


def test_ranked_keys_sorted_descending(vault_path):
    record_access(vault_path, "LOW")
    record_access(vault_path, "HIGH")
    record_access(vault_path, "HIGH")
    record_access(vault_path, "HIGH")
    record_access(vault_path, "MID")
    record_access(vault_path, "MID")
    result = ranked_keys(vault_path)
    keys = [k for k, _ in result]
    assert keys == ["HIGH", "MID", "LOW"]


def test_ranked_keys_includes_scores(vault_path):
    record_access(vault_path, "X")
    record_access(vault_path, "X")
    pairs = dict(ranked_keys(vault_path))
    assert pairs["X"] == 2


def test_reset_score_returns_true_for_existing_key(vault_path):
    record_access(vault_path, "TOKEN")
    assert reset_score(vault_path, "TOKEN") is True


def test_reset_score_returns_false_for_missing_key(vault_path):
    assert reset_score(vault_path, "GHOST") is False


def test_reset_score_zeroes_out_key(vault_path):
    record_access(vault_path, "TOKEN")
    reset_score(vault_path, "TOKEN")
    assert get_score(vault_path, "TOKEN") == 0


def test_record_access_empty_key_raises(vault_path):
    with pytest.raises(RankingError):
        record_access(vault_path, "")


def test_get_score_empty_key_raises(vault_path):
    with pytest.raises(RankingError):
        get_score(vault_path, "")


def test_reset_score_empty_key_raises(vault_path):
    with pytest.raises(RankingError):
        reset_score(vault_path, "")
