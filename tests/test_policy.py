"""Tests for envault.policy."""

import pytest

from envault.policy import (
    PolicyError,
    enforce,
    get_rule,
    list_rules,
    remove_rule,
    set_rule,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "vault.enc")


def test_set_and_get_rule(vault_path):
    set_rule(vault_path, "require_ttl", True)
    assert get_rule(vault_path, "require_ttl") is True


def test_get_missing_rule_returns_none(vault_path):
    assert get_rule(vault_path, "require_ttl") is None


def test_set_invalid_rule_raises(vault_path):
    with pytest.raises(PolicyError, match="Unknown policy rule"):
        set_rule(vault_path, "nonexistent_rule", True)


def test_list_rules_empty(vault_path):
    assert list_rules(vault_path) == {}


def test_list_rules_returns_all(vault_path):
    set_rule(vault_path, "require_ttl", True)
    set_rule(vault_path, "deny_plaintext_export", True)
    rules = list_rules(vault_path)
    assert rules["require_ttl"] is True
    assert rules["deny_plaintext_export"] is True


def test_remove_existing_rule(vault_path):
    set_rule(vault_path, "require_ttl", True)
    result = remove_rule(vault_path, "require_ttl")
    assert result is True
    assert get_rule(vault_path, "require_ttl") is None


def test_remove_missing_rule_returns_false(vault_path):
    assert remove_rule(vault_path, "require_ttl") is False


def test_enforce_max_secret_length_passes(vault_path):
    set_rule(vault_path, "max_secret_length", 20)
    enforce(vault_path, "MY_KEY", "short")


def test_enforce_max_secret_length_fails(vault_path):
    set_rule(vault_path, "max_secret_length", 5)
    with pytest.raises(PolicyError, match="max_secret_length"):
        enforce(vault_path, "MY_KEY", "this_is_too_long")


def test_enforce_allowed_key_pattern_passes(vault_path):
    set_rule(vault_path, "allowed_key_pattern", r"[A-Z][A-Z0-9_]*")
    enforce(vault_path, "VALID_KEY", "value")


def test_enforce_allowed_key_pattern_fails(vault_path):
    set_rule(vault_path, "allowed_key_pattern", r"[A-Z][A-Z0-9_]*")
    with pytest.raises(PolicyError, match="allowed_key_pattern"):
        enforce(vault_path, "invalid-key", "value")


def test_enforce_no_rules_always_passes(vault_path):
    enforce(vault_path, "ANY_KEY", "any_value" * 100)


def test_overwrite_rule(vault_path):
    set_rule(vault_path, "max_secret_length", 10)
    set_rule(vault_path, "max_secret_length", 50)
    assert get_rule(vault_path, "max_secret_length") == 50
