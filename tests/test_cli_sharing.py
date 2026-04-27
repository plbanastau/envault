"""Integration tests for the sharing CLI commands."""

import json
from click.testing import CliRunner
import pytest

from envault.vault import Vault
from envault.sharing import create_bundle
from envault.cli_sharing import share_group


VAULT_PASS = "vault-pass"
SHARE_PASS = "bundle-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def src_vault_path(tmp_path):
    path = tmp_path / "src.vault"
    v = Vault(str(path), password=VAULT_PASS)
    v.set("FOO", "bar")
    v.set("BAZ", "qux")
    v.save()
    return str(path)


@pytest.fixture
def dst_vault_path(tmp_path):
    path = tmp_path / "dst.vault"
    v = Vault(str(path), password=VAULT_PASS)
    v.save()
    return str(path)


def test_create_cmd_outputs_bundle(runner, src_vault_path):
    result = runner.invoke(
        share_group,
        ["create", "--vault-path", src_vault_path, "--password", VAULT_PASS, "--share-password", SHARE_PASS],
        input=f"{SHARE_PASS}\n{SHARE_PASS}\n",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_import_cmd_restores_keys(runner, src_vault_path, dst_vault_path):
    src_vault = Vault(src_vault_path, password=VAULT_PASS)
    bundle = create_bundle(src_vault, SHARE_PASS)

    result = runner.invoke(
        share_group,
        [
            "import", bundle,
            "--vault-path", dst_vault_path,
            "--password", VAULT_PASS,
            "--share-password", SHARE_PASS,
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "2 key(s)" in result.output

    dst_vault = Vault(dst_vault_path, password=VAULT_PASS)
    assert dst_vault.get("FOO") == "bar"
    assert dst_vault.get("BAZ") == "qux"


def test_import_cmd_wrong_share_password_fails(runner, src_vault_path, dst_vault_path):
    src_vault = Vault(src_vault_path, password=VAULT_PASS)
    bundle = create_bundle(src_vault, SHARE_PASS)

    result = runner.invoke(
        share_group,
        [
            "import", bundle,
            "--vault-path", dst_vault_path,
            "--password", VAULT_PASS,
            "--share-password", "wrong-pass",
        ],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
