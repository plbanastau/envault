# Policy Enforcement

envault supports configurable **policies** per vault to enforce security rules on secrets and key names.

## Overview

Policies are stored in a `.envault_policy.json` file alongside the vault file. Rules are evaluated whenever a secret is written.

## Available Rules

| Rule | Type | Description |
|------|------|-------------|
| `require_ttl` | `bool` | Require all secrets to have a TTL set |
| `deny_plaintext_export` | `bool` | Prevent exporting secrets as plain `.env` |
| `max_secret_length` | `int` | Maximum allowed character length for any secret value |
| `allowed_key_pattern` | `str` | Regex pattern that all key names must fully match |

## Usage

### Set a rule

```python
from envault.policy import set_rule

set_rule("/path/to/vault.enc", "max_secret_length", 256)
set_rule("/path/to/vault.enc", "allowed_key_pattern", r"[A-Z][A-Z0-9_]*")
```

### Enforce rules before writing

```python
from envault.policy import enforce

enforce("/path/to/vault.enc", "MY_API_KEY", "supersecret")
# Raises PolicyError if any rule is violated
```

### List all rules

```python
from envault.policy import list_rules

rules = list_rules("/path/to/vault.enc")
print(rules)
# {'max_secret_length': 256, 'allowed_key_pattern': '[A-Z][A-Z0-9_]*'}
```

### Remove a rule

```python
from envault.policy import remove_rule

remove_rule("/path/to/vault.enc", "require_ttl")
```

## Errors

All violations raise `envault.policy.PolicyError` with a descriptive message indicating which rule was violated and why.

## Integration

The `enforce()` function should be called in `vault.set()` to ensure policies are checked on every write operation.
