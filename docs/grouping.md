# Secret Grouping

Envault lets you organise secrets into named **groups**, making it easy to work with related keys as a unit — for example, all database secrets, all third-party API keys, or all secrets belonging to a specific service.

## Concepts

- A **group** is a named collection of secret keys stored in your vault.
- A key can belong to **multiple groups** simultaneously.
- Groups are stored in a sidecar file next to your vault file (e.g. `.myproject.groups.json`).

## CLI Usage

### Add a key to a group

```bash
envault group add infra DB_HOST
envault group add infra DB_PORT
```

### List all groups

```bash
envault group list
```

### Show keys in a group

```bash
envault group show infra
# DB_HOST
# DB_PORT
```

### Remove a key from a group

```bash
envault group remove infra DB_HOST
```

### Delete an entire group

```bash
envault group delete infra
```

### Find which groups contain a key

```bash
envault group of DB_HOST
# infra
# web
```

## Python API

```python
from pathlib import Path
from envault.grouping import (
    add_to_group, remove_from_group, get_group,
    list_groups, delete_group, groups_for_key,
)

vault_path = Path(".envault/production.vault")

add_to_group(vault_path, "database", "DB_HOST")
add_to_group(vault_path, "database", "DB_PASSWORD")

print(get_group(vault_path, "database"))   # ['DB_HOST', 'DB_PASSWORD']
print(list_groups(vault_path))             # ['database']
print(groups_for_key(vault_path, "DB_HOST"))  # ['database']
```

## Errors

`GroupingError` is raised when:

- The group name is empty.
- The key name is empty.
