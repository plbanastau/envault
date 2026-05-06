"""Tests for envault.cli_grouping."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_grouping import group_group
from envault.grouping import add_to_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    vp = tmp_path / "test.vault"
    vp.touch()
    return vp


def _invoke(runner, vault_path, args):
    return runner.invoke(group_group, args, obj={"vault_path": vault_path})


def test_add_cmd_success(runner, vault_path):
    result = _invoke(runner, vault_path, ["add", "infra", "DB_HOST"])
    assert result.exit_code == 0
    assert "Added 'DB_HOST' to group 'infra'" in result.output


def test_add_cmd_empty_group_raises(runner, vault_path):
    result = _invoke(runner, vault_path, ["add", "", "DB_HOST"])
    assert result.exit_code != 0


def test_list_cmd_empty(runner, vault_path):
    result = _invoke(runner, vault_path, ["list"])
    assert result.exit_code == 0
    assert "No groups defined" in result.output


def test_list_cmd_shows_groups(runner, vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    add_to_group(vault_path, "web", "PORT")
    result = _invoke(runner, vault_path, ["list"])
    assert "infra" in result.output
    assert "web" in result.output


def test_show_cmd_lists_keys(runner, vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    add_to_group(vault_path, "infra", "DB_PORT")
    result = _invoke(runner, vault_path, ["show", "infra"])
    assert "DB_HOST" in result.output
    assert "DB_PORT" in result.output


def test_show_cmd_empty_group(runner, vault_path):
    result = _invoke(runner, vault_path, ["show", "ghost"])
    assert result.exit_code == 0
    assert "empty or does not exist" in result.output


def test_remove_cmd_success(runner, vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    result = _invoke(runner, vault_path, ["remove", "infra", "DB_HOST"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_cmd_missing_key(runner, vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    result = _invoke(runner, vault_path, ["remove", "infra", "MISSING"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_delete_cmd_success(runner, vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    result = _invoke(runner, vault_path, ["delete", "infra"])
    assert result.exit_code == 0
    assert "Deleted group 'infra'" in result.output


def test_delete_cmd_missing_group(runner, vault_path):
    result = _invoke(runner, vault_path, ["delete", "ghost"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_of_cmd_lists_groups(runner, vault_path):
    add_to_group(vault_path, "infra", "DB_HOST")
    add_to_group(vault_path, "web", "DB_HOST")
    result = _invoke(runner, vault_path, ["of", "DB_HOST"])
    assert "infra" in result.output
    assert "web" in result.output


def test_of_cmd_no_groups(runner, vault_path):
    result = _invoke(runner, vault_path, ["of", "ORPHAN"])
    assert result.exit_code == 0
    assert "not in any group" in result.output
