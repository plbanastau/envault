# Scoping

Scoping lets you associate secrets with named environments (e.g. `dev`, `staging`, `prod`). This makes it easy to query which secrets belong to a particular environment and to keep your vault organised across deployment targets.

## Concepts

- A **scope** is a free-form string label (e.g. `dev`, `prod`, `eu-west`).
- A single secret **key** can belong to multiple scopes simultaneously.
- Scopes are stored in a sidecar file (`.envault_scopes.json`) next to the vault file.

## Python API

```python
from envault.scoping import (
    assign_scope, remove_scope, get_scopes,
    keys_in_scope, list_scopes, clear_scopes,
)

vault = "my_project/vault.json"

# Assign a key to one or more scopes
assign_scope(vault, "DB_PASSWORD", "prod")
assign_scope(vault, "DB_PASSWORD", "staging")

# Retrieve scopes for a key
print(get_scopes(vault, "DB_PASSWORD"))   # ['prod', 'staging']

# Find all keys in a scope
print(keys_in_scope(vault, "prod"))       # ['DB_PASSWORD', ...]

# List every scope currently in use
print(list_scopes(vault))                 # ['prod', 'staging']

# Remove a single scope assignment
remove_scope(vault, "DB_PASSWORD", "staging")

# Remove all scope assignments for a key
clear_scopes(vault, "DB_PASSWORD")
```

## CLI

```
Usage: envault scope [COMMAND]

Commands:
  assign  Assign a key to a scope
  remove  Remove a key from a scope
  list    List all scopes in use
  show    Show all keys in a given scope
  clear   Remove all scope assignments for a key
```

### Examples

```bash
# Assign DB_URL to prod
envault scope assign DB_URL prod

# Show all keys in prod
envault scope show prod

# List all scopes
envault scope list

# Remove DB_URL from prod
envault scope remove DB_URL prod

# Clear every scope for DB_URL
envault scope clear DB_URL
```

## Error Handling

`ScopingError` is raised when:

- An empty key or scope name is provided to `assign_scope`.

All other operations degrade gracefully (e.g. `remove_scope` returns `False` instead of raising when the assignment does not exist).
