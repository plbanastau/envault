"""Tests for envault.formatting."""

import pytest

from envault.formatting import (
    FormattingError,
    apply_format,
    get_format,
    list_formats,
    remove_format,
    set_format,
)


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault.enc")


# --- set_format / get_format ---

def test_set_and_get_format(vault_path):
    set_format(vault_path, "API_KEY", "upper")
    assert get_format(vault_path, "API_KEY") == "upper"


def test_get_format_returns_none_for_unknown_key(vault_path):
    assert get_format(vault_path, "MISSING") is None


def test_set_format_empty_key_raises(vault_path):
    with pytest.raises(FormattingError, match="empty"):
        set_format(vault_path, "", "upper")


def test_set_format_invalid_fmt_raises(vault_path):
    with pytest.raises(FormattingError, match="Unknown format"):
        set_format(vault_path, "MY_KEY", "rot13")


def test_set_format_overwrites_previous(vault_path):
    set_format(vault_path, "TOKEN", "upper")
    set_format(vault_path, "TOKEN", "lower")
    assert get_format(vault_path, "TOKEN") == "lower"


# --- remove_format ---

def test_remove_format_returns_true_when_exists(vault_path):
    set_format(vault_path, "KEY", "strip")
    assert remove_format(vault_path, "KEY") is True
    assert get_format(vault_path, "KEY") is None


def test_remove_format_returns_false_when_missing(vault_path):
    assert remove_format(vault_path, "GHOST") is False


# --- list_formats ---

def test_list_formats_empty_initially(vault_path):
    assert list_formats(vault_path) == {}


def test_list_formats_returns_all_entries(vault_path):
    set_format(vault_path, "A", "upper")
    set_format(vault_path, "B", "lower")
    result = list_formats(vault_path)
    assert result == {"A": "upper", "B": "lower"}


# --- apply_format ---

def test_apply_upper():
    assert apply_format("hello", "upper") == "HELLO"


def test_apply_lower():
    assert apply_format("WORLD", "lower") == "world"


def test_apply_strip():
    assert apply_format("  spaced  ", "strip") == "spaced"


def test_apply_base64_check_valid():
    import base64
    encoded = base64.b64encode(b"secret").decode()
    assert apply_format(encoded, "base64_check") == encoded


def test_apply_base64_check_invalid_raises():
    with pytest.raises(FormattingError, match="base64"):
        apply_format("not!!base64!!", "base64_check")


def test_apply_json_check_valid():
    val = '{"key": "value"}'
    assert apply_format(val, "json_check") == val


def test_apply_json_check_invalid_raises():
    with pytest.raises(FormattingError, match="JSON"):
        apply_format("{bad json", "json_check")


def test_apply_url_check_valid():
    url = "https://example.com/api"
    assert apply_format(url, "url_check") == url


def test_apply_url_check_invalid_raises():
    with pytest.raises(FormattingError, match="URL"):
        apply_format("ftp://old-school.net", "url_check")


def test_apply_unknown_format_raises():
    with pytest.raises(FormattingError, match="Unknown"):
        apply_format("value", "nonexistent")
