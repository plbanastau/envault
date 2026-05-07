"""Vault secret compression — optionally compress secret values before encryption."""

from __future__ import annotations

import base64
import zlib
from dataclasses import dataclass
from typing import Dict, List

COMPRESSION_MARKER = "z1:"


class CompressionError(Exception):
    """Raised when compression or decompression fails."""


@dataclass
class CompressionStats:
    key: str
    original_size: int
    compressed_size: int

    @property
    def ratio(self) -> float:
        if self.original_size == 0:
            return 1.0
        return self.compressed_size / self.original_size

    @property
    def saved_bytes(self) -> int:
        return self.original_size - self.compressed_size

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CompressionStats(key={self.key!r}, "
            f"original={self.original_size}, "
            f"compressed={self.compressed_size}, "
            f"ratio={self.ratio:.2%})"
        )


def compress_value(value: str) -> str:
    """Compress a string value and return a marked, base64-encoded string."""
    if not isinstance(value, str):
        raise CompressionError("value must be a string")
    raw = value.encode("utf-8")
    compressed = zlib.compress(raw, level=9)
    encoded = base64.b64encode(compressed).decode("ascii")
    return COMPRESSION_MARKER + encoded


def decompress_value(value: str) -> str:
    """Decompress a previously compressed value. Returns plain values unchanged."""
    if not value.startswith(COMPRESSION_MARKER):
        return value
    encoded = value[len(COMPRESSION_MARKER):]
    try:
        compressed = base64.b64decode(encoded)
        raw = zlib.decompress(compressed)
        return raw.decode("utf-8")
    except Exception as exc:
        raise CompressionError(f"failed to decompress value: {exc}") from exc


def is_compressed(value: str) -> bool:
    """Return True if the value was produced by compress_value."""
    return value.startswith(COMPRESSION_MARKER)


def compress_secrets(secrets: Dict[str, str]) -> Dict[str, CompressionStats]:
    """Compress all values in a secrets dict in-place and return per-key stats."""
    stats: Dict[str, CompressionStats] = {}
    for key, value in list(secrets.items()):
        original_size = len(value.encode("utf-8"))
        compressed = compress_value(value)
        compressed_size = len(compressed.encode("utf-8"))
        secrets[key] = compressed
        stats[key] = CompressionStats(
            key=key,
            original_size=original_size,
            compressed_size=compressed_size,
        )
    return stats


def decompress_secrets(secrets: Dict[str, str]) -> None:
    """Decompress all compressed values in a secrets dict in-place."""
    for key, value in list(secrets.items()):
        secrets[key] = decompress_value(value)


def list_compressed_keys(secrets: Dict[str, str]) -> List[str]:
    """Return a sorted list of keys whose values are currently compressed."""
    return sorted(k for k, v in secrets.items() if is_compressed(v))
