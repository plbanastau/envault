"""Tests for envault.validation."""
import pytest

from envault.validation import (
    ValidationError,
    ValidationResult,
    available_rules,
    validate_value,
)


# ---------------------------------------------------------------------------
# available_rules
# ---------------------------------------------------------------------------

def test_available_rules_returns_list():
    rules = available_rules()
    assert isinstance(rules, list)
    assert len(rules) > 0


def test_available_rules_contains_expected_names():
    rules = available_rules()
    for name in ("non_empty", "no_whitespace", "printable_ascii", "min_length", "max_length", "regex"):
        assert name in rules


# ---------------------------------------------------------------------------
# non_empty
# ---------------------------------------------------------------------------

def test_non_empty_passes_for_non_empty_value():
    result = validate_value("KEY", "hello", [{"rule": "non_empty"}])
    assert result.passed is True
    assert result.violations == []


def test_non_empty_fails_for_empty_string():
    result = validate_value("KEY", "", [{"rule": "non_empty"}])
    assert result.passed is False
    assert len(result.violations) == 1


# ---------------------------------------------------------------------------
# no_whitespace
# ---------------------------------------------------------------------------

def test_no_whitespace_passes_for_clean_value():
    result = validate_value("KEY", "value", [{"rule": "no_whitespace"}])
    assert result.passed is True


def test_no_whitespace_fails_for_leading_space():
    result = validate_value("KEY", " value", [{"rule": "no_whitespace"}])
    assert result.passed is False


def test_no_whitespace_fails_for_trailing_space():
    result = validate_value("KEY", "value ", [{"rule": "no_whitespace"}])
    assert result.passed is False


# ---------------------------------------------------------------------------
# printable_ascii
# ---------------------------------------------------------------------------

def test_printable_ascii_passes_for_plain_string():
    result = validate_value("KEY", "Hello123!", [{"rule": "printable_ascii"}])
    assert result.passed is True


def test_printable_ascii_fails_for_non_ascii():
    result = validate_value("KEY", "caf\u00e9", [{"rule": "printable_ascii"}])
    assert result.passed is False


# ---------------------------------------------------------------------------
# min_length / max_length
# ---------------------------------------------------------------------------

def test_min_length_passes_when_value_long_enough():
    result = validate_value("KEY", "abcdefgh", [{"rule": "min_length", "min": 8}])
    assert result.passed is True


def test_min_length_fails_when_value_too_short():
    result = validate_value("KEY", "abc", [{"rule": "min_length", "min": 8}])
    assert result.passed is False


def test_max_length_passes_when_value_short_enough():
    result = validate_value("KEY", "hi", [{"rule": "max_length", "max": 10}])
    assert result.passed is True


def test_max_length_fails_when_value_too_long():
    result = validate_value("KEY", "a" * 20, [{"rule": "max_length", "max": 10}])
    assert result.passed is False


# ---------------------------------------------------------------------------
# regex
# ---------------------------------------------------------------------------

def test_regex_passes_when_pattern_matches():
    result = validate_value("KEY", "user@example.com", [{"rule": "regex", "pattern": r".+@.+\..+"}])
    assert result.passed is True


def test_regex_fails_when_pattern_does_not_match():
    result = validate_value("KEY", "not-an-email", [{"rule": "regex", "pattern": r".+@.+\..+"}])
    assert result.passed is False


# ---------------------------------------------------------------------------
# multiple rules & error cases
# ---------------------------------------------------------------------------

def test_multiple_violations_collected():
    result = validate_value("KEY", "", [
        {"rule": "non_empty"},
        {"rule": "min_length", "min": 5},
    ])
    assert result.passed is False
    assert len(result.violations) == 2


def test_unknown_rule_raises_validation_error():
    with pytest.raises(ValidationError, match="Unknown validation rule"):
        validate_value("KEY", "value", [{"rule": "does_not_exist"}])


def test_non_string_value_raises_validation_error():
    with pytest.raises(ValidationError, match="must be a string"):
        validate_value("KEY", 123, [{"rule": "non_empty"}])  # type: ignore[arg-type]


def test_result_key_is_preserved():
    result = validate_value("MY_SECRET", "ok", [{"rule": "non_empty"}])
    assert result.key == "MY_SECRET"
