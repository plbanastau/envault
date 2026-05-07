# Formatting

envault supports optional **format rules** for secret keys. A format rule
describes how a value should be transformed or validated when it is applied.

## Supported formats

| Name | Behaviour |
|------|-----------|
| `upper` | Convert value to upper-case |
| `lower` | Convert value to lower-case |
| `strip` | Strip leading/trailing whitespace |
| `base64_check` | Validate that the value is valid base-64 (no transform) |
| `json_check` | Validate that the value is valid JSON (no transform) |
| `url_check` | Validate that the value starts with `http://` or `https://` |

## CLI usage

### Assign a format rule

```bash
envault format set API_KEY upper --vault prod.enc
```

### View the rule for a key

```bash
envault format get API_KEY --vault prod.enc
```

### Apply a rule to a value

```bash
envault format apply API_KEY "my-secret" --vault prod.enc
# MY-SECRET
```

### Remove a rule

```bash
envault format remove API_KEY --vault prod.enc
```

### List all rules

```bash
envault format list --vault prod.enc
```

## Python API

```python
from envault.formatting import set_format, get_format, apply_format, remove_format, list_formats

vault = "prod.enc"

# Assign
set_format(vault, "DATABASE_URL", "url_check")

# Read back
fmt = get_format(vault, "DATABASE_URL")  # "url_check"

# Apply
apply_format("https://db.example.com", "url_check")  # returns value unchanged

# Remove
remove_format(vault, "DATABASE_URL")

# List all
rules = list_formats(vault)  # {"KEY": "fmt", ...}
```

## Error handling

`FormattingError` is raised when:

- An unknown format name is supplied to `set_format` or `apply_format`.
- An empty key is passed to `set_format`.
- A value fails a validation-only check (`base64_check`, `json_check`,
  `url_check`).
