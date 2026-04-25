"""Vault model: manages a collection of encrypted environment variables."""

import json
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt


class Vault:
    """Represents an encrypted vault storing key-value environment variables."""

    def __init__(self, path: Path, password: str):
        self.path = path
        self.password = password
        self._data: Dict[str, str] = {}

    def load(self) -> None:
        """Load and decrypt vault from disk. Creates empty vault if file missing."""
        if not self.path.exists():
            self._data = {}
            return
        raw = self.path.read_text(encoding="utf-8").strip()
        if not raw:
            self._data = {}
            return
        plaintext = decrypt(raw, self.password)
        self._data = json.loads(plaintext)

    def save(self) -> None:
        """Encrypt and persist vault to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        plaintext = json.dumps(self._data)
        ciphertext = encrypt(plaintext, self.password)
        self.path.write_text(ciphertext, encoding="utf-8")

    def set(self, key: str, value: str) -> None:
        """Set an environment variable in the vault."""
        self._data[key] = value

    def get(self, key: str) -> Optional[str]:
        """Retrieve an environment variable by key."""
        return self._data.get(key)

    def delete(self, key: str) -> bool:
        """Delete a key. Returns True if it existed."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    def list_keys(self) -> Dict[str, str]:
        """Return a copy of all stored key-value pairs."""
        return dict(self._data)
