# Access Control

envault supports **per-key, per-actor permissions** so you can record which
team members (or service accounts) are allowed to read or write each secret.

> Note: envault's access control is *advisory* — it records intent and can be
> checked by automation or code-review tooling.  Enforcement is up to your
> deployment pipeline.

---

## Permissions

| Permission | Meaning |
|------------|---------|
| `read`     | Actor may decrypt and use the value |
| `write`    | Actor may set / rotate the value |

---

## Python API

```python
from envault.access import grant, revoke, get_permissions, list_acl, ACCESS_READ, ACCESS_WRITE

vault_path = ".envault/production.vault"

# Grant alice read access to DB_URL
grant(vault_path, "DB_URL", "alice", ACCESS_READ)

# Grant bob full access to API_KEY
grant(vault_path, "API_KEY", "bob", ACCESS_READ)
grant(vault_path, "API_KEY", "bob", ACCESS_WRITE)

# Check what alice can do with DB_URL
perms = get_permissions(vault_path, "DB_URL", "alice")
# → {'read'}

# Inspect the full ACL for a key
acl = list_acl(vault_path, "DB_URL")
# → {'read': ['alice'], 'write': []}

# Revoke a permission
revoke(vault_path, "API_KEY", "bob", ACCESS_WRITE)
```

---

## Storage

Permissions are persisted in a JSON sidecar file named
`.envault_access.json` in the same directory as the vault file.

```json
{
  "API_KEY": {
    "read": ["alice", "bob"],
    "write": ["alice"]
  },
  "DB_URL": {
    "read": ["alice"]
  }
}
```

The file is human-readable and safe to commit to version control alongside
your (encrypted) vault.

---

## Errors

`AccessError` is raised when an unknown permission string is supplied.
All other operations are non-destructive and return `False` / empty
collections instead of raising when nothing matches.
