# Key Remapping

The **remapping** module lets you define per-vault rules that rename secret keys
at export time without changing how they are stored internally.

## Why remapping?

Different deployment targets often expect different environment variable names.
For example, your vault might store a secret as `DB_PASS`, while one application
expects `DATABASE_PASSWORD` and another expects `POSTGRES_PASSWORD`. Instead of
duplicate secrets or manual renaming, define a remap rule once.

## Python API

```python
from envault.remapping import set_remap, get_remap, remove_remap, list_remaps, apply_remaps

vault = "path/to/my.vault"

# Store a mapping: DB_PASS → DATABASE_PASSWORD
set_remap(vault, "DB_PASS", "DATABASE_PASSWORD")

# Retrieve the target name for a key
print(get_remap(vault, "DB_PASS"))  # "DATABASE_PASSWORD"

# Apply all remaps to a dict of decrypted secrets
exported = apply_remaps(vault, {"DB_PASS": "s3cr3t", "API_KEY": "xyz"})
# → {"DATABASE_PASSWORD": "s3cr3t", "API_KEY": "xyz"}

# List all active remaps
print(list_remaps(vault))
# → {"DB_PASS": "DATABASE_PASSWORD"}

# Remove a remap rule
remove_remap(vault, "DB_PASS")
```

## Behaviour notes

- **Unmapped keys** are exported under their original name.
- **Overwriting**: calling `set_remap` again for the same key replaces the
  previous target.
- **Collision**: if a remapped target name is identical to another key already
  in the secrets dict, the remapped value takes precedence.
- Remapping rules are stored in a sidecar file `<vault>.remapping.json` next to
  the vault file.

## Errors

`RemappingError` is raised when:
- `key` or `target` is an empty string in `set_remap`.
