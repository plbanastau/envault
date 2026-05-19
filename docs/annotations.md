# Annotations

The **annotations** module lets you attach free-form notes to individual secret
keys stored in a vault.  Notes are stored in a sidecar JSON file and never
encrypted, so they are readable without the vault password.

## Storage

Annotations are written to:

```
<vault-dir>/.envault/annotations.json
```

The file is a plain JSON object mapping key names to note strings.

## API

### `set_annotation(vault_path, key, note) -> str`

Attach *note* to *key*.  Overwrites any existing note.  Raises
`AnnotationError` if *key* or *note* is empty.

```python
from envault.annotations import set_annotation

set_annotation("/project/.vault", "DB_URL", "Primary Postgres connection string")
```

### `get_annotation(vault_path, key) -> str | None`

Return the note for *key*, or `None` if no annotation has been set.

```python
from envault.annotations import get_annotation

note = get_annotation("/project/.vault", "DB_URL")
```

### `remove_annotation(vault_path, key) -> bool`

Delete the annotation for *key*.  Returns `True` if the annotation existed,
`False` otherwise.

### `list_annotations(vault_path) -> dict[str, str]`

Return all annotations as a `{key: note}` mapping sorted alphabetically by key.

```python
from envault.annotations import list_annotations

for key, note in list_annotations("/project/.vault").items():
    print(f"{key}: {note}")
```

## Errors

| Exception | Cause |
|---|---|
| `AnnotationError` | Empty key or empty note passed to `set_annotation` |
