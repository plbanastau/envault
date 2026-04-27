"""Tests for envault.sharing module."""

import time
import pytest

from envault.vault import Vault
from envault.sharing import create_bundle, import_bundle, SharingError


SHARE_PASSWORD = "share-secret-42"


@pytest.fixture
def src_vault(tmp_path):
    path = tmp_path / "src.vault"
    v = Vault(str(path), password="vault-pass")
    v.set("DB_HOST", "localhost")
    v.set("API_KEY", "abc123")
    v.set("TOKEN", "tok-xyz")
    v.save()
    return v


@pytest.fixture
def dst_vault(tmp_path):
    path = tmp_path / "dst.vault"
    v = Vault(str(path), password="other-pass")
    v.save()
    return v


def test_create_bundle_returns_string(src_vault):
    bundle = create_bundle(src_vault, SHARE_PASSWORD)
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_import_bundle_restores_all_keys(src_vault, dst_vault):
    bundle = create_bundle(src_vault, SHARE_PASSWORD)
    imported = import_bundle(dst_vault, bundle, SHARE_PASSWORD)
    assert set(imported) == {"DB_HOST", "API_KEY", "TOKEN"}
    assert dst_vault.get("DB_HOST") == "localhost"
    assert dst_vault.get("API_KEY") == "abc123"


def test_create_bundle_with_specific_keys(src_vault, dst_vault):
    bundle = create_bundle(src_vault, SHARE_PASSWORD, keys=["DB_HOST", "TOKEN"])
    imported = import_bundle(dst_vault, bundle, SHARE_PASSWORD)
    assert set(imported) == {"DB_HOST", "TOKEN"}
    assert dst_vault.get("API_KEY") is None


def test_create_bundle_missing_key_raises(src_vault):
    with pytest.raises(SharingError, match="not found"):
        create_bundle(src_vault, SHARE_PASSWORD, keys=["NONEXISTENT"])


def test_import_bundle_wrong_password_raises(src_vault, dst_vault):
    bundle = create_bundle(src_vault, SHARE_PASSWORD)
    with pytest.raises(SharingError, match="Invalid share password"):
        import_bundle(dst_vault, bundle, "wrong-password")


def test_import_bundle_corrupted_raises(dst_vault):
    with pytest.raises(SharingError, match="Malformed bundle"):
        import_bundle(dst_vault, "not-a-valid-bundle!!", SHARE_PASSWORD)


def test_import_bundle_expired_raises(src_vault, dst_vault):
    bundle = create_bundle(src_vault, SHARE_PASSWORD, expires_in=-1)
    with pytest.raises(SharingError, match="expired"):
        import_bundle(dst_vault, bundle, SHARE_PASSWORD)


def test_bundle_each_call_produces_unique_output(src_vault):
    b1 = create_bundle(src_vault, SHARE_PASSWORD)
    b2 = create_bundle(src_vault, SHARE_PASSWORD)
    assert b1 != b2
