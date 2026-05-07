"""CLI commands for managing value format rules."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.formatting import (
    FormattingError,
    apply_format,
    get_format,
    list_formats,
    remove_format,
    set_format,
)


@click.group("format", help="Manage value format rules for secrets.")
def format_group() -> None:
    pass


@format_group.command("set")
@click.argument("key")
@click.argument("fmt")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def set_cmd(key: str, fmt: str, vault: str, password: str) -> None:
    """Assign format rule FMT to KEY."""
    get_vault(vault, password)  # validates password / creates vault
    try:
        set_format(vault, key, fmt)
        click.echo(f"Format '{fmt}' assigned to '{key}'.")
    except FormattingError as exc:
        raise click.ClickException(str(exc))


@format_group.command("get")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def get_cmd(key: str, vault: str, password: str) -> None:
    """Show the format rule assigned to KEY."""
    get_vault(vault, password)
    fmt = get_format(vault, key)
    if fmt is None:
        click.echo(f"No format rule set for '{key}'.")
    else:
        click.echo(fmt)


@format_group.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def remove_cmd(key: str, vault: str, password: str) -> None:
    """Remove the format rule for KEY."""
    get_vault(vault, password)
    removed = remove_format(vault, key)
    if removed:
        click.echo(f"Format rule removed for '{key}'.")
    else:
        click.echo(f"No format rule found for '{key}'.")


@format_group.command("list")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def list_cmd(vault: str, password: str) -> None:
    """List all format rules in the vault."""
    get_vault(vault, password)
    rules = list_formats(vault)
    if not rules:
        click.echo("No format rules defined.")
        return
    for key, fmt in sorted(rules.items()):
        click.echo(f"{key}: {fmt}")


@format_group.command("apply")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default="vault.enc", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def apply_cmd(key: str, value: str, vault: str, password: str) -> None:
    """Apply the format rule for KEY to VALUE and print the result."""
    get_vault(vault, password)
    fmt = get_format(vault, key)
    if fmt is None:
        raise click.ClickException(f"No format rule set for '{key}'.")
    try:
        result = apply_format(value, fmt)
        click.echo(result)
    except FormattingError as exc:
        raise click.ClickException(str(exc))
