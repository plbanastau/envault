"""Search and filter secrets within a vault by key pattern or metadata."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from typing import List, Optional

from envault.vault import Vault


class SearchError(Exception):
    """Raised when a search operation fails."""


@dataclass
class SearchResult:
    key: str
    matched_by: str  # 'key_glob', 'key_regex'

    def __repr__(self) -> str:  # pragma: no cover
        return f"SearchResult(key={self.key!r}, matched_by={self.matched_by!r})"


def search_by_glob(vault: Vault, password: str, pattern: str) -> List[SearchResult]:
    """Return keys whose names match a Unix shell-style glob pattern."""
    all_keys = vault.list_keys()
    results = []
    for key in sorted(all_keys):
        if fnmatch.fnmatch(key, pattern):
            results.append(SearchResult(key=key, matched_by="key_glob"))
    return results


def search_by_regex(vault: Vault, password: str, pattern: str) -> List[SearchResult]:
    """Return keys whose names match a regular expression."""
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise SearchError(f"Invalid regex pattern {pattern!r}: {exc}") from exc

    all_keys = vault.list_keys()
    results = []
    for key in sorted(all_keys):
        if compiled.search(key):
            results.append(SearchResult(key=key, matched_by="key_regex"))
    return results


def search(vault: Vault, password: str, pattern: str, use_regex: bool = False) -> List[SearchResult]:
    """Unified search entry-point. Delegates to glob or regex search."""
    if use_regex:
        return search_by_regex(vault, password, pattern)
    return search_by_glob(vault, password, pattern)
