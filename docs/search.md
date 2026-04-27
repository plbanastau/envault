# Secret Search

`envault` supports searching your vault's keys by **glob pattern** or **regular expression**, making it easy to locate secrets in large vaults.

## CLI Usage

```bash
# Glob search (default)
envault search "AWS_*"

# Regex search
envault search --regex "^DB_.*_URL$"
```

## Glob Patterns

Glob matching follows Unix shell conventions via Python's `fnmatch`:

| Pattern | Matches |
|---|---|
| `AWS_*` | Any key starting with `AWS_` |
| `*_URL` | Any key ending with `_URL` |
| `*SECRET*` | Any key containing `SECRET` |
| `DB_?` | `DB_` followed by exactly one character |

Patterns are **case-sensitive**.

## Regex Patterns

Use `--regex` / `-r` for full Python `re` syntax:

```bash
envault search --regex "^(AWS|GCP)_"
```

An invalid regex will produce an error message and exit with a non-zero status.

## Python API

```python
from envault.vault import Vault
from envault.search import search, search_by_glob, search_by_regex

vault = Vault(".vault.json")

# Glob
results = search_by_glob(vault, "my-password", "AWS_*")
for r in results:
    print(r.key)  # e.g. AWS_ACCESS_KEY_ID

# Regex
results = search_by_regex(vault, "my-password", r"_URL$")

# Unified
results = search(vault, "my-password", r"_URL$", use_regex=True)
```

Each result is a `SearchResult` dataclass:

```python
@dataclass
class SearchResult:
    key: str
    matched_by: str  # 'key_glob' or 'key_regex'
```

## Notes

- Results are always returned in **alphabetical order** by key name.
- The search never decrypts secret values — only key names are inspected.
