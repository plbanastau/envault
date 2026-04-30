# Secret Pinning

envault lets you **pin** a snapshot of a secret's current value under a named
label. Pins are stored separately from the live vault data, so rotating or
updating a secret never overwrites your saved pins.

## Use cases

- Preserve the database URL used in a specific release.
- Keep a "last-known-good" copy of credentials before a rotation.
- Audit which value was active at a given point in time.

## Python API

```python
from pathlib import Path
from envault.pinning import pin_secret, get_pin, list_pins, delete_pin

vault_path = Path(".envault/prod.json")
password   = "my-master-password"

# Pin the current value of DB_URL
entry = pin_secret(vault_path, password, "DB_URL", label="v2.3.0")
print(entry)
# {'label': 'v2.3.0', 'value': 'postgres://...', 'pinned_at': '2024-...'}

# Retrieve a pinned value later
value = get_pin(vault_path, "DB_URL", "v2.3.0")

# List all pins for a key (sorted oldest → newest)
for pin in list_pins(vault_path, "DB_URL"):
    print(pin["label"], pin["pinned_at"])

# Remove a pin
deleted = delete_pin(vault_path, "DB_URL", "v2.3.0")
```

## Storage

Pins are saved in a sidecar file next to the vault:

```
.envault/
  prod.json          ← live vault
  prod.pins.json     ← pin store
```

The pin store is a plain JSON file; each key maps to a dict of
`{ label → { label, value, pinned_at } }` entries.

## Errors

| Situation | Exception |
|---|---|
| Key not found in vault | `PinningError` |
| Label already exists for that key | `PinningError` |
| Empty label string | `PinningError` |
