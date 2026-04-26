"""Import environment variables into a vault from various sources.

Supports importing from:
  - .env files (dotenv format)
  - Shell export statements
  - JSON files
  - The current OS environment
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple


def _parse_dotenv_line(line: str) -> Optional[Tuple[str, str]]:
    """Parse a single line from a .env file.

    Handles:
      - Blank lines and comments (returns None)
      - Optional 'export' prefix
      - Quoted values (single or double quotes)
      - Inline comments after unquoted values

    Returns a (key, value) tuple or None if the line should be skipped.
    """
    line = line.strip()

    # Skip blank lines and comments
    if not line or line.startswith("#"):
        return None

    # Strip optional 'export' prefix
    if line.startswith("export "):
        line = line[len("export "):].strip()

    if "=" not in line:
        return None

    key, _, raw_value = line.partition("=")
    key = key.strip()

    if not key:
        return None

    raw_value = raw_value.strip()

    # Handle double-quoted values
    if raw_value.startswith('"') and raw_value.endswith('"'):
        value = raw_value[1:-1]
        # Unescape common escape sequences inside double quotes
        value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
    # Handle single-quoted values (no escape processing)
    elif raw_value.startswith("'") and raw_value.endswith("'"):
        value = raw_value[1:-1]
    else:
        # Strip inline comments for unquoted values
        value = re.sub(r"\s+#.*$", "", raw_value).strip()

    return key, value


def import_dotenv(path: str) -> Dict[str, str]:
    """Parse a .env file and return a dict of key/value pairs.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary of environment variable names to their string values.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    result: Dict[str, str] = {}
    with file_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            parsed = _parse_dotenv_line(line)
            if parsed is not None:
                key, value = parsed
                result[key] = value

    return result


def import_json(path: str) -> Dict[str, str]:
    """Parse a JSON file containing a flat key/value mapping.

    Args:
        path: Path to the JSON file.

    Returns:
        Dictionary of environment variable names to their string values.
        Non-string values are coerced to strings.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON is not a top-level object.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with file_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError("JSON file must contain a top-level object (dict).")

    return {str(k): str(v) for k, v in data.items()}


def import_env(keys: Optional[list] = None) -> Dict[str, str]:
    """Read variables from the current OS environment.

    Args:
        keys: Optional list of specific variable names to import.
              If None, all environment variables are returned.

    Returns:
        Dictionary of environment variable names to their values.
    """
    if keys is not None:
        return {k: os.environ[k] for k in keys if k in os.environ}
    return dict(os.environ)
