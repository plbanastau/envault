"""Tests for envault.export module."""

import json

import pytest

from envault.export import export_dotenv, export_json, export_shell, render, SUPPORTED_FORMATS


SAMPLE = {"DB_HOST": "localhost", "API_KEY": "s3cr3t", "PORT": "5432"}


# ---------------------------------------------------------------------------
# export_dotenv
# ---------------------------------------------------------------------------

def test_dotenv_keys_are_sorted():
    result = export_dotenv(SAMPLE)
    lines = result.strip().splitlines()
    keys = [line.split("=")[0] for line in lines]
    assert keys == sorted(keys)


def test_dotenv_no_export_prefix_by_default():
    result = export_dotenv(SAMPLE)
    assert not any(line.startswith("export ") for line in result.splitlines())


def test_dotenv_with_export_keyword():
    result = export_dotenv(SAMPLE, export_keyword=True)
    assert all(line.startswith("export ") for line in result.strip().splitlines())


def test_dotenv_empty_secrets():
    assert export_dotenv({}) == ""


def test_dotenv_quotes_value_with_spaces():
    result = export_dotenv({"MSG": "hello world"})
    assert 'MSG="hello world"' in result


def test_dotenv_plain_value_not_quoted():
    result = export_dotenv({"KEY": "simple"})
    assert "KEY=simple" in result


# ---------------------------------------------------------------------------
# export_shell
# ---------------------------------------------------------------------------

def test_shell_always_has_export_prefix():
    result = export_shell(SAMPLE)
    assert all(line.startswith("export ") for line in result.strip().splitlines())


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

def test_json_is_valid():
    result = export_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_json_keys_are_sorted():
    result = export_json(SAMPLE)
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(SAMPLE.keys())


# ---------------------------------------------------------------------------
# render dispatcher
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fmt", SUPPORTED_FORMATS)
def test_render_accepts_all_supported_formats(fmt):
    output = render(SAMPLE, fmt)
    assert isinstance(output, str)
    assert len(output) > 0


def test_render_raises_on_unknown_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        render(SAMPLE, "yaml")
