"""Tests for envault.rotation."""

from __future__ import annotations

import pytest

from envault.rotation import RotationError, rotate_key, verify_password
from envault.vault import Vault


OLD_PASSWORD = "old-secret-pass"
NEW_PASSWORD = "new-secret-pass"


@pytest.fixture()
def tmp_vault(tmp_path):
    path = tmp_path / "test.vault"
    v = Vault(str(path))
    v.set("API_KEY", "abc123", OLD_PASSWORD)
    v.set("DB_URL", "postgres://localhost/db", OLD_PASSWORD)
    return v


def test_rotate_key_re_encrypts_all_secrets(tmp_vault):
    result = rotate_key(tmp_vault, OLD_PASSWORD, NEW_PASSWORD)

    assert result["rotated"] == 2
    assert result["failed"] == 0


def test_rotated_secrets_readable_with_new_password(tmp_vault):
    rotate_key(tmp_vault, OLD_PASSWORD, NEW_PASSWORD)

    assert tmp_vault.get("API_KEY", NEW_PASSWORD) == "abc123"
    assert tmp_vault.get("DB_URL", NEW_PASSWORD) == "postgres://localhost/db"


def test_rotated_secrets_not_readable_with_old_password(tmp_vault):
    rotate_key(tmp_vault, OLD_PASSWORD, NEW_PASSWORD)

    with pytest.raises(Exception):
        tmp_vault.get("API_KEY", OLD_PASSWORD)


def test_rotate_key_wrong_old_password_raises(tmp_vault):
    with pytest.raises(RotationError):
        rotate_key(tmp_vault, "wrong-password", NEW_PASSWORD)


def test_rotate_key_empty_vault(tmp_path):
    path = tmp_path / "empty.vault"
    v = Vault(str(path))
    result = rotate_key(v, OLD_PASSWORD, NEW_PASSWORD)

    assert result == {"rotated": 0, "failed": 0}


def test_verify_password_correct(tmp_vault):
    assert verify_password(tmp_vault, OLD_PASSWORD) is True


def test_verify_password_wrong(tmp_vault):
    assert verify_password(tmp_vault, "totally-wrong") is False


def test_verify_password_empty_vault(tmp_path):
    path = tmp_path / "empty.vault"
    v = Vault(str(path))
    # No secrets — nothing to fail on
    assert verify_password(v, "any-password") is True
