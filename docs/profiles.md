# Profiles

Profiles let you define named subsets of secret keys for a vault. This is useful when different environments (e.g. `production`, `staging`, `dev`) need access to different sets of variables.

## Concepts

A **profile** is a named list of key names stored alongside your vault file. Profiles do not store values — they only record which keys belong to a logical group.

## API

### `save_profile(vault_path, name, keys)`

Create or overwrite a profile.

```python
from envault.profiles import save_profile

save_profile(vault_path, "production", ["DB_URL", "SECRET_KEY", "API_TOKEN"])
```

### `get_profile(vault_path, name)`

Return the sorted list of keys for a profile. Raises `ProfilesError` if the profile does not exist.

```python
from envault.profiles import get_profile

keys = get_profile(vault_path, "production")
# ["API_TOKEN", "DB_URL", "SECRET_KEY"]
```

### `list_profiles(vault_path)`

Return all profile names in alphabetical order.

```python
from envault.profiles import list_profiles

names = list_profiles(vault_path)
# ["dev", "production", "staging"]
```

### `delete_profile(vault_path, name)`

Delete a profile. Returns `True` if deleted, `False` if it did not exist.

```python
from envault.profiles import delete_profile

delete_profile(vault_path, "staging")
```

### `rename_profile(vault_path, old_name, new_name)`

Rename an existing profile. Raises `ProfilesError` if the source does not exist or the target name is already taken.

```python
from envault.profiles import rename_profile

rename_profile(vault_path, "dev", "development")
```

## Storage

Profiles are persisted in a JSON sidecar file next to the vault:

```
my_project.vault
my_project.profiles.json   ← profile data stored here
```

## Errors

All error conditions raise `ProfilesError` with a descriptive message:

| Condition | Message |
|---|---|
| Empty profile name | `Profile name must not be empty.` |
| Empty key list | `Profile must contain at least one key.` |
| Profile not found | `Profile '<name>' does not exist.` |
| Rename target exists | `Profile '<name>' already exists.` |
