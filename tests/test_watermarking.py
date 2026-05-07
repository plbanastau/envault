"""Tests for envault.watermarking."""

import pytest

from envault.watermarking import (
    WatermarkError,
    embed,
    list_watermarks,
    remove,
    verify,
)


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "vault" / "secrets.db"
    p.parent.mkdir(parents=True)
    p.touch()
    return str(p)


def test_embed_returns_original_value(vault_path):
    result = embed(vault_path, "API_KEY", "s3cr3t", "alice")
    assert result == "s3cr3t"


def test_verify_returns_actor_after_embed(vault_path):
    embed(vault_path, "API_KEY", "s3cr3t", "alice")
    actor = verify(vault_path, "API_KEY", "s3cr3t")
    assert actor == "alice"


def test_verify_unknown_key_returns_none(vault_path):
    assert verify(vault_path, "UNKNOWN", "value") is None


def test_verify_tampered_value_raises(vault_path):
    embed(vault_path, "DB_PASS", "original", "bob")
    with pytest.raises(WatermarkError, match="tampered"):
        verify(vault_path, "DB_PASS", "modified")


def test_embed_empty_key_raises(vault_path):
    with pytest.raises(WatermarkError, match="key"):
        embed(vault_path, "", "value", "alice")


def test_embed_empty_actor_raises(vault_path):
    with pytest.raises(WatermarkError, match="actor"):
        embed(vault_path, "KEY", "value", "")


def test_remove_existing_watermark_returns_true(vault_path):
    embed(vault_path, "TOKEN", "abc", "carol")
    assert remove(vault_path, "TOKEN") is True


def test_remove_missing_watermark_returns_false(vault_path):
    assert remove(vault_path, "NONEXISTENT") is False


def test_verify_after_remove_returns_none(vault_path):
    embed(vault_path, "TOKEN", "abc", "carol")
    remove(vault_path, "TOKEN")
    assert verify(vault_path, "TOKEN", "abc") is None


def test_list_watermarks_empty(vault_path):
    assert list_watermarks(vault_path) == {}


def test_list_watermarks_shows_all_actors(vault_path):
    embed(vault_path, "KEY_A", "v1", "alice")
    embed(vault_path, "KEY_B", "v2", "bob")
    wm = list_watermarks(vault_path)
    assert wm == {"KEY_A": "alice", "KEY_B": "bob"}


def test_overwrite_watermark_updates_actor(vault_path):
    embed(vault_path, "KEY", "val", "alice")
    embed(vault_path, "KEY", "val", "dave")
    assert verify(vault_path, "KEY", "val") == "dave"
