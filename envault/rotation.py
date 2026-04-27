"""Key rotation support for envault vaults."""

from __future__ import annotations

from typing import TYPE_CHECKING

from envault.crypto import decrypt, encrypt

if TYPE_CHECKING:
    from envault.vault import Vault


class RotationError(Exception):
    """Raised when key rotation fails."""


def rotate_key(
    vault: "Vault",
    old_password: str,
    new_password: str,
) -> dict[str, int]:
    """Re-encrypt all secrets in *vault* with *new_password*.

    The vault is loaded with *old_password*, every stored ciphertext is
    decrypted and immediately re-encrypted under *new_password*, and the
    vault is saved.  Returns a summary dict with the number of rotated
    keys and any keys that failed.

    Raises ``RotationError`` if *old_password* cannot decrypt any key
    (fast-fail before writing anything).
    """
    if not vault.secrets:
        return {"rotated": 0, "failed": 0}

    plaintext: dict[str, str] = {}
    for key, ciphertext in vault.secrets.items():
        try:
            plaintext[key] = decrypt(ciphertext, old_password)
        except Exception as exc:  # noqa: BLE001
            raise RotationError(
                f"Failed to decrypt '{key}' with the old password: {exc}"
            ) from exc

    failed = 0
    new_secrets: dict[str, str] = {}
    for key, value in plaintext.items():
        try:
            new_secrets[key] = encrypt(value, new_password)
        except Exception:  # noqa: BLE001
            failed += 1

    vault.secrets = new_secrets
    vault.save(new_password)

    return {"rotated": len(new_secrets), "failed": failed}


def verify_password(vault: "Vault", password: str) -> bool:
    """Return *True* if *password* can decrypt every secret in *vault*."""
    for ciphertext in vault.secrets.values():
        try:
            decrypt(ciphertext, password)
        except Exception:  # noqa: BLE001
            return False
    return True
