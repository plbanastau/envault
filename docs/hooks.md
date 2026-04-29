# Lifecycle Hooks

envault supports **lifecycle hooks** — shell commands that are automatically executed when certain vault operations occur.

## Supported Events

| Event | Triggered When |
|---|---|
| `pre_set` | Before a secret is written |
| `post_set` | After a secret is written |
| `pre_delete` | Before a secret is deleted |
| `post_delete` | After a secret is deleted |
| `post_rotate` | After the vault master key is rotated |

## Registering a Hook

```python
from envault.hooks import register_hook
from pathlib import Path

vault = Path("myproject.vault")
register_hook(vault, "post_set", "echo 'Secret updated!'")
```

Hooks for the same event are stored in order and executed sequentially.

## Listing Hooks

```python
from envault.hooks import list_hooks

# All events
hooks = list_hooks(vault)

# Single event
hooks = list_hooks(vault, "post_set")
```

## Removing a Hook

```python
from envault.hooks import unregister_hook

removed = unregister_hook(vault, "post_set", "echo 'Secret updated!'")
# True if found and removed, False if not found
```

## Firing Hooks Programmatically

```python
from envault.hooks import fire

executed = fire(vault, "post_set", env={"ENVAULT_KEY": "MY_SECRET"})
```

Custom environment variables passed via `env` are merged with the current process environment before each hook runs.

If any hook exits with a non-zero status, a `HooksError` is raised and subsequent hooks in the same event are **not** executed.

## Storage

Hooks are stored as a JSON sidecar file alongside the vault:

```
myproject.vault
myproject.hooks.json   ← hook definitions
```

## Error Handling

```python
from envault.hooks import HooksError

try:
    fire(vault, "post_rotate")
except HooksError as e:
    print(f"Hook failed: {e}")
```
