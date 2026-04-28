# Templates

Templates let you define named collections of environment variable keys with
optional default values. Use them to scaffold new vaults or environments
consistently without manually re-entering the same keys each time.

## Saving a template

```bash
envault template save web HOST=localhost PORT=8080 DEBUG=false
```

This stores a template called `web` with three keys and their defaults inside
the `.templates.json` sidecar file next to your vault.

## Listing templates

```bash
envault template list
```

## Showing a template

```bash
envault template show web
# HOST=localhost
# PORT=8080
# DEBUG=false
```

## Applying a template

Applying a template writes any **missing** keys into the vault using their
default values.

```bash
envault template apply web
```

To overwrite keys that already exist:

```bash
envault template apply web --overwrite
```

## Deleting a template

```bash
envault template delete web
```

## Python API

```python
from envault.templates import save_template, apply_template, list_templates

save_template("my.vault", "web", {"HOST": "localhost", "PORT": "8080"})

# Returns list of keys written
written = apply_template("my.vault", "web", password="s3cr3t")

print(list_templates("my.vault"))  # ['web']
```

## Storage

Templates are stored in a JSON sidecar file alongside your vault:

```
my.vault
my.templates.json   ← template definitions live here
```

The file is **not encrypted** — templates only store key names and placeholder
defaults, never secret values.
