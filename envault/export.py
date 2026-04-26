"""Export vault secrets to various shell-compatible formats."""

from __future__ import annotations

from typing import Dict, Optional


SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_dotenv(secrets: Dict[str, str], export_keyword: bool = False) -> str:
    """Render secrets as a .env file.

    Args:
        secrets: Mapping of key -> plaintext value.
        export_keyword: Prefix each line with ``export`` so the file can be
            sourced directly in bash/zsh.

    Returns:
        A newline-separated string of KEY=VALUE pairs.
    """
    prefix = "export " if export_keyword else ""
    lines = [f"{prefix}{key}={_quote_value(value)}" for key, value in sorted(secrets.items())]
    return "\n".join(lines) + ("\n" if lines else "")


def export_shell(secrets: Dict[str, str]) -> str:
    """Render secrets as ``export KEY=VALUE`` statements (bash/zsh)."""
    return export_dotenv(secrets, export_keyword=True)


def export_json(secrets: Dict[str, str], indent: int = 2) -> str:
    """Render secrets as a JSON object."""
    import json

    return json.dumps(dict(sorted(secrets.items())), indent=indent) + "\n"


def render(secrets: Dict[str, str], fmt: str, **kwargs) -> str:
    """Dispatch to the appropriate renderer.

    Args:
        secrets: Decrypted key/value pairs.
        fmt: One of ``dotenv``, ``shell``, or ``json``.
        **kwargs: Extra options forwarded to the renderer.

    Raises:
        ValueError: If *fmt* is not a supported format.

    Returns:
        Rendered string.
    """
    if fmt == "dotenv":
        return export_dotenv(secrets, **kwargs)
    if fmt == "shell":
        return export_shell(secrets)
    if fmt == "json":
        return export_json(secrets, **kwargs)
    raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")


def _quote_value(value: str) -> str:
    """Wrap *value* in double-quotes if it contains whitespace or special chars."""
    needs_quoting = any(ch in value for ch in (" ", "\t", "\n", "'", '"', "$", "`", ";", "&", "|", ">", "<"))
    if needs_quoting:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value
