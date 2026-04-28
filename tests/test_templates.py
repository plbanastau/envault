"""Tests for envault.templates module."""
import pytest
from pathlib import Path

from envault.templates import (
    TemplateError,
    apply_template,
    delete_template,
    get_template,
    list_templates,
    save_template,
)
from envault.vault import Vault


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def test_save_and_get_template(vault_path):
    save_template(vault_path, "web", {"HOST": "localhost", "PORT": "8080"})
    result = get_template(vault_path, "web")
    assert result == {"HOST": "localhost", "PORT": "8080"}


def test_get_missing_template_raises(vault_path):
    with pytest.raises(TemplateError, match="not found"):
        get_template(vault_path, "nonexistent")


def test_save_empty_name_raises(vault_path):
    with pytest.raises(TemplateError, match="empty"):
        save_template(vault_path, "", {"KEY": "val"})


def test_list_templates_empty(vault_path):
    assert list_templates(vault_path) == []


def test_list_templates_sorted(vault_path):
    save_template(vault_path, "zebra", {})
    save_template(vault_path, "alpha", {})
    save_template(vault_path, "mango", {})
    assert list_templates(vault_path) == ["alpha", "mango", "zebra"]


def test_delete_existing_template(vault_path):
    save_template(vault_path, "db", {"DB_HOST": ""})
    assert delete_template(vault_path, "db") is True
    assert "db" not in list_templates(vault_path)


def test_delete_missing_template_returns_false(vault_path):
    assert delete_template(vault_path, "ghost") is False


def test_overwrite_template(vault_path):
    save_template(vault_path, "web", {"PORT": "80"})
    save_template(vault_path, "web", {"PORT": "443", "SSL": "true"})
    result = get_template(vault_path, "web")
    assert result["PORT"] == "443"
    assert result["SSL"] == "true"


def test_apply_template_writes_defaults(vault_path):
    password = "secret"
    save_template(vault_path, "base", {"APP_ENV": "production", "DEBUG": "false"})
    written = apply_template(vault_path, "base", password)
    assert sorted(written) == ["APP_ENV", "DEBUG"]
    vault = Vault(vault_path, password)
    assert vault.get("APP_ENV") == "production"
    assert vault.get("DEBUG") == "false"


def test_apply_template_skips_existing_without_overwrite(vault_path):
    password = "secret"
    vault = Vault(vault_path, password)
    vault.set("APP_ENV", "staging")
    save_template(vault_path, "base", {"APP_ENV": "production", "DEBUG": "false"})
    written = apply_template(vault_path, "base", password, overwrite=False)
    assert "APP_ENV" not in written
    assert vault.get("APP_ENV") == "staging"


def test_apply_template_with_overwrite(vault_path):
    password = "secret"
    vault = Vault(vault_path, password)
    vault.set("APP_ENV", "staging")
    save_template(vault_path, "base", {"APP_ENV": "production"})
    written = apply_template(vault_path, "base", password, overwrite=True)
    assert "APP_ENV" in written
    assert Vault(vault_path, password).get("APP_ENV") == "production"
