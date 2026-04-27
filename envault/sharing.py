"""Secure sharing of vault secrets via encrypted export bundles."""

import json
import os
import time
from base64 import urlsafe_b64encode, urlsafe_b64decode
from typing import Optional

from envault.crypto import derive_key, encrypt, decrypt
from envault.vault import Vault


class SharingError(Exception):
    pass


def create_bundle(
    vault: Vault,
    share_password: str,
    keys: Optional[list] = None,
    expires_in: Optional[int] = None,
) -> str:
    """Create an encrypted bundle of selected (or all) secrets.

    Args:
        vault: The source Vault instance.
        share_password: Password used to encrypt the bundle.
        keys: List of secret keys to include. None means all keys.
        expires_in: Seconds until the bundle expires. None means no expiry.

    Returns:
        A base64-encoded encrypted bundle string.
    """
    secrets = {}
    available_keys = vault.list_keys()
    target_keys = keys if keys is not None else available_keys

    for key in target_keys:
        value = vault.get(key)
        if value is None:
            raise SharingError(f"Key '{key}' not found in vault.")
        secrets[key] = value

    payload = {
        "secrets": secrets,
        "created_at": time.time(),
        "expires_at": (time.time() + expires_in) if expires_in else None,
    }

    plaintext = json.dumps(payload)
    salt = os.urandom(16)
    key = derive_key(share_password, salt)
    token = encrypt(plaintext, key)

    bundle = {
        "salt": urlsafe_b64encode(salt).decode(),
        "token": token,
    }
    raw = json.dumps(bundle).encode()
    return urlsafe_b64encode(raw).decode()


def import_bundle(vault: Vault, bundle_str: str, share_password: str) -> list:
    """Decrypt and import secrets from a bundle into the vault.

    Args:
        vault: The destination Vault instance.
        bundle_str: The base64-encoded encrypted bundle.
        share_password: Password used to decrypt the bundle.

    Returns:
        List of keys that were imported.
    """
    try:
        raw = urlsafe_b64decode(bundle_str.encode())
        bundle = json.loads(raw)
        salt = urlsafe_b64decode(bundle["salt"].encode())
        token = bundle["token"]
    except Exception as exc:
        raise SharingError(f"Malformed bundle: {exc}") from exc

    key = derive_key(share_password, salt)
    try:
        plaintext = decrypt(token, key)
    except Exception as exc:
        raise SharingError("Invalid share password or corrupted bundle.") from exc

    payload = json.loads(plaintext)

    expires_at = payload.get("expires_at")
    if expires_at and time.time() > expires_at:
        raise SharingError("Bundle has expired.")

    imported = []
    for k, v in payload["secrets"].items():
        vault.set(k, v)
        imported.append(k)

    vault.save()
    return imported
