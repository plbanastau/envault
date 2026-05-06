# Key Labeling

The **labeling** feature lets you attach human-readable display names to secret
keys stored in a vault. Labels are stored in a sidecar file
(`.envault/labels.json`) alongside the vault and are never encrypted — they are
meant for display purposes only.

## Python API

```python
from envault.labeling import set_label, get_label, remove_label, list_labels, keys_with_label

vault = "production.enc"

# Attach a label
set_label(vault, "DB_PASSWORD", "PostgreSQL master password")

# Retrieve a label
print(get_label(vault, "DB_PASSWORD"))  # "PostgreSQL master password"

# List all labels (sorted by key)
for entry in list_labels(vault):
    print(entry["key"], "->", entry["label"])

# Find keys by label
keys = keys_with_label(vault, "Sensitive")

# Remove a label
remove_label(vault, "DB_PASSWORD")
```

## CLI

### Set a label

```bash
envault label set DB_PASSWORD "PostgreSQL master password"
```

### Get a label

```bash
envault label get DB_PASSWORD
```

### Remove a label

```bash
envault label remove DB_PASSWORD
```

### List all labels

```bash
envault label list
```

### Find keys by label

```bash
envault label find "Sensitive"
```

## Storage

Labels are stored in `.envault/labels.json` relative to the vault file:

```json
{
  "API_KEY": "Third-party API key",
  "DB_PASSWORD": "PostgreSQL master password"
}
```

## Notes

- Labels are purely cosmetic and have no effect on encryption or access control.
- Setting a label for a key that does not exist in the vault is allowed; this
  can be useful when pre-configuring a vault schema.
- Labels are **not** included in encrypted exports or bundles.
