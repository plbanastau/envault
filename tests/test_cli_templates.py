"""Tests for CLI template commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_templates import template_group
from envault.vault import Vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def test_save_and_list(runner, vault_path):
    result = runner.invoke(
        template_group,
        ["save", "web", "HOST=localhost", "PORT=8080", "--vault", vault_path],
    )
    assert result.exit_code == 0
    assert "saved" in result.output

    result = runner.invoke(template_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0
    assert "web" in result.output


def test_list_empty(runner, vault_path):
    result = runner.invoke(template_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0
    assert "No templates" in result.output


def test_show_template(runner, vault_path):
    runner.invoke(
        template_group,
        ["save", "db", "DB_HOST=localhost", "DB_PORT=5432", "--vault", vault_path],
    )
    result = runner.invoke(template_group, ["show", "db", "--vault", vault_path])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DB_PORT=5432" in result.output


def test_show_missing_template(runner, vault_path):
    result = runner.invoke(template_group, ["show", "ghost", "--vault", vault_path])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_delete_template(runner, vault_path):
    runner.invoke(template_group, ["save", "tmp", "--vault", vault_path])
    result = runner.invoke(template_group, ["delete", "tmp", "--vault", vault_path])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_missing_template(runner, vault_path):
    result = runner.invoke(template_group, ["delete", "ghost", "--vault", vault_path])
    assert result.exit_code != 0


def test_apply_template(runner, vault_path):
    runner.invoke(
        template_group,
        ["save", "base", "APP_ENV=production", "--vault", vault_path],
    )
    result = runner.invoke(
        template_group,
        ["apply", "base", "--vault", vault_path, "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "APP_ENV" in result.output
    vault = Vault(vault_path, "secret")
    assert vault.get("APP_ENV") == "production"


def test_apply_template_no_overwrite_message(runner, vault_path):
    runner.invoke(
        template_group,
        ["save", "base", "APP_ENV=production", "--vault", vault_path],
    )
    # Apply once
    runner.invoke(
        template_group,
        ["apply", "base", "--vault", vault_path, "--password", "secret"],
    )
    # Apply again without overwrite
    result = runner.invoke(
        template_group,
        ["apply", "base", "--vault", vault_path, "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "No keys written" in result.output
