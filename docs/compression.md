# Secret Compression

`envault` supports optional compression of secret values before they are encrypted and stored. This is useful when managing large secrets such as certificates, JSON blobs, or lengthy connection strings.

## How It Works

Compression uses **zlib** (deflate, level 9) followed by **base64** encoding. A short marker prefix (`z1:`) is prepended so that envault can detect and transparently decompress values at read time.

```
plaintext  →  zlib.compress  →  base64.encode  →  "z1:<encoded>"
```

Compressed values are then passed through the normal encryption pipeline — compression happens *before* encryption.

## API Reference

### `compress_value(value: str) -> str`

Compress a single string value. Returns a marked, base64-encoded string.

```python
from envault.compression import compress_value, decompress_value

compressed = compress_value("postgres://user:secret@localhost/db")
original   = decompress_value(compressed)  # round-trips cleanly
```

### `decompress_value(value: str) -> str`

Decompress a value produced by `compress_value`. If the value does not carry the compression marker it is returned unchanged, making the function safe to call unconditionally.

### `is_compressed(value: str) -> bool`

Return `True` if the value was produced by `compress_value`.

### `compress_secrets(secrets: dict) -> dict[str, CompressionStats]`

Compress **all** values in a `{key: value}` dict **in-place**. Returns a mapping of key → `CompressionStats`.

```python
from envault.compression import compress_secrets

secrets = {"CERT": long_pem_string, "KEY": long_key_string}
stats = compress_secrets(secrets)
print(stats["CERT"].ratio)       # e.g. 0.42
print(stats["CERT"].saved_bytes) # bytes saved
```

### `decompress_secrets(secrets: dict) -> None`

Decompress all compressed values in a dict in-place.

### `list_compressed_keys(secrets: dict) -> list[str]`

Return a sorted list of keys whose values are currently in compressed form.

## `CompressionStats`

| Field             | Type    | Description                          |
|-------------------|---------|--------------------------------------|
| `key`             | `str`   | Secret key name                      |
| `original_size`   | `int`   | Byte size before compression         |
| `compressed_size` | `int`   | Byte size after compression+encoding |
| `ratio`           | `float` | `compressed / original` (lower = better) |
| `saved_bytes`     | `int`   | `original - compressed`              |

## Errors

`CompressionError` is raised when:

- A non-string value is passed to `compress_value`.
- A value with the compression marker cannot be decompressed (corrupted data).
