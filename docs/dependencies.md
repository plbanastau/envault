# Secret Dependencies

Envault can track dependency relationships between secrets. This lets you
perform impact analysis — for example, to see which services would be
affected if a particular secret were rotated or deleted.

## Concepts

- **Dependency**: Secret `A` *depends on* secret `B` when `A`'s value or
  behaviour is influenced by `B` (e.g. a connection string that embeds a
  password).
- **Dependent**: The inverse relationship. If `A` depends on `B`, then `B`
  has `A` as a dependent.

## Python API

```python
from envault.dependencies import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    list_all,
)

vault = "myproject.vault"

# Mark that DATABASE_URL relies on DB_PASSWORD
add_dependency(vault, "DATABASE_URL", "DB_PASSWORD")

# Find everything DATABASE_URL depends on
get_dependencies(vault, "DATABASE_URL")
# => ["DB_PASSWORD"]

# Find everything that would be affected if DB_PASSWORD changed
get_dependents(vault, "DB_PASSWORD")
# => ["DATABASE_URL"]

# Remove a dependency
remove_dependency(vault, "DATABASE_URL", "DB_PASSWORD")

# Dump the entire dependency graph
list_all(vault)
# => {"SERVICE_URL": ["API_KEY", "HOST"]}
```

## Errors

| Exception | Reason |
|-----------|--------|
| `DependencyError` | Empty key/depends_on, or a secret depending on itself |

## Storage

Dependency data is stored alongside the vault file as
`<vault>.dependencies.json`. It is a plain JSON object mapping each key to
the sorted list of keys it depends on.

## Use Cases

- Before rotating a secret, call `get_dependents` to list all affected keys.
- After a bulk import, call `list_all` to audit the dependency graph.
- Integrate with CI to block deletions of secrets that still have dependents.
