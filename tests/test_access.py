"""Tests for envault.access — per-key permission management."""

import pytest

from envault.access import (
    ACCESS_READ,
    ACCESS_WRITE,
    AccessError,
    grant,
    get_permissions,
    list_acl,
    revoke,
    _access_path,
)


@pytest.fixture()
def vault_path(tmp_path):
    return tmp_path / "vault.env"


# ---------------------------------------------------------------------------
# grant / get_permissions
# ---------------------------------------------------------------------------

def test_grant_read_permission(vault_path):
    grant(vault_path, "DB_URL", "alice", ACCESS_READ)
    perms = get_permissions(vault_path, "DB_URL", "alice")
    assert ACCESS_READ in perms


def test_grant_write_permission(vault_path):
    grant(vault_path, "API_KEY", "bob", ACCESS_WRITE)
    perms = get_permissions(vault_path, "API_KEY", "bob")
    assert ACCESS_WRITE in perms


def test_grant_both_permissions(vault_path):
    grant(vault_path, "SECRET", "carol", ACCESS_READ)
    grant(vault_path, "SECRET", "carol", ACCESS_WRITE)
    perms = get_permissions(vault_path, "SECRET", "carol")
    assert perms == {ACCESS_READ, ACCESS_WRITE}


def test_grant_is_idempotent(vault_path):
    grant(vault_path, "KEY", "alice", ACCESS_READ)
    grant(vault_path, "KEY", "alice", ACCESS_READ)
    acl = list_acl(vault_path, "KEY")
    assert acl[ACCESS_READ].count("alice") == 1


def test_grant_unknown_permission_raises(vault_path):
    with pytest.raises(AccessError, match="Unknown permission"):
        grant(vault_path, "KEY", "alice", "delete")


def test_get_permissions_no_acl_returns_empty(vault_path):
    assert get_permissions(vault_path, "MISSING", "nobody") == set()


# ---------------------------------------------------------------------------
# revoke
# ---------------------------------------------------------------------------

def test_revoke_existing_permission_returns_true(vault_path):
    grant(vault_path, "TOKEN", "dave", ACCESS_READ)
    changed = revoke(vault_path, "TOKEN", "dave", ACCESS_READ)
    assert changed is True
    assert ACCESS_READ not in get_permissions(vault_path, "TOKEN", "dave")


def test_revoke_nonexistent_permission_returns_false(vault_path):
    changed = revoke(vault_path, "TOKEN", "eve", ACCESS_WRITE)
    assert changed is False


def test_revoke_does_not_affect_other_actors(vault_path):
    grant(vault_path, "KEY", "alice", ACCESS_READ)
    grant(vault_path, "KEY", "bob", ACCESS_READ)
    revoke(vault_path, "KEY", "alice", ACCESS_READ)
    assert ACCESS_READ in get_permissions(vault_path, "KEY", "bob")


# ---------------------------------------------------------------------------
# list_acl / persistence
# ---------------------------------------------------------------------------

def test_list_acl_returns_all_actors(vault_path):
    grant(vault_path, "DB", "alice", ACCESS_READ)
    grant(vault_path, "DB", "bob", ACCESS_READ)
    grant(vault_path, "DB", "carol", ACCESS_WRITE)
    acl = list_acl(vault_path, "DB")
    assert sorted(acl[ACCESS_READ]) == ["alice", "bob"]
    assert acl[ACCESS_WRITE] == ["carol"]


def test_access_file_created_on_first_grant(vault_path):
    assert not _access_path(vault_path).exists()
    grant(vault_path, "KEY", "alice", ACCESS_READ)
    assert _access_path(vault_path).exists()


def test_actors_stored_sorted(vault_path):
    for actor in ["zara", "alice", "mike"]:
        grant(vault_path, "KEY", actor, ACCESS_READ)
    acl = list_acl(vault_path, "KEY")
    assert acl[ACCESS_READ] == sorted(acl[ACCESS_READ])
