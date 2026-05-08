# Secret Versioning

envault tracks every encrypted value that has ever been stored for a key,
allowing you to audit or restore previous values without touching the live
vault.

## How it works

Each time a secret is written through the vault, a version snapshot of the
**encrypted** value is appended to `.envault/versions.json` inside the same
directory as the vault file.  The plaintext is never stored in the version
log — only the ciphertext that is already present in the vault itself.

## API

```python
from envault.versioning import (
    record_version,
    list_versions,
    get_version,
    purge_versions,
)
```

### `record_version(vault_path, key, encrypted_value, actor="system")`

Append a new version entry for `key`.  Returns the entry dict:

```json
{
  "version": 3,
  "encrypted_value": "gAAAAA...",
  "timestamp": 1718000000.123,
  "actor": "alice"
}
```

### `list_versions(vault_path, key)`

Return all recorded versions for `key` in chronological order (oldest
first).  Returns an empty list if no versions exist.

### `get_version(vault_path, key, version)`

Fetch a specific version (1-based index).  Raises `VersioningError` if
the key has no history or the version number is out of range.

### `purge_versions(vault_path, key)`

Delete all version history for `key`.  Returns the number of entries
removed.  This cannot be undone.

## Example

```python
from pathlib import Path
from envault.vault import Vault
from envault.versioning import record_version, list_versions, get_version

vault = Vault("production.vault", password="s3cr3t")

# Whenever you set a key, record its encrypted form:
encrypted = vault._raw_encrypted("DATABASE_URL")  # internal helper
record_version("production.vault", "DATABASE_URL", encrypted, actor="deploy-bot")

# List all versions:
for v in list_versions("production.vault", "DATABASE_URL"):
    print(v["version"], v["timestamp"], v["actor"])

# Retrieve a specific version:
entry = get_version("production.vault", "DATABASE_URL", 2)
print(entry["encrypted_value"])
```

## Storage format

Versions are persisted in `.envault/versions.json` as a JSON object keyed
by secret name:

```json
{
  "DATABASE_URL": [
    {"version": 1, "encrypted_value": "gAAAAA...", "timestamp": 1718000000.0, "actor": "system"},
    {"version": 2, "encrypted_value": "gAAAAB...", "timestamp": 1718003600.0, "actor": "alice"}
  ]
}
```
