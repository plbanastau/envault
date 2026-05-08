"""CLI commands for managing secret scopes."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.scoping import (
    ScopingError,
    assign_scope,
    clear_scopes,
    get_scopes,
    keys_in_scope,
    list_scopes,
    remove_scope,
)


@click.group("scope")
def scope_group() -> None:
    """Manage scopes for secrets (e.g. dev, staging, prod)."""


@scope_group.command("assign")
@click.argument("key")
@click.argument("scope")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def assign_cmd(key: str, scope: str, vault_path: str) -> None:
    """Assign KEY to SCOPE."""
    try:
        assign_scope(vault_path, key, scope)
        click.echo(f"Assigned '{key}' to scope '{scope}'.")
    except ScopingError as exc:
        raise click.ClickException(str(exc)) from exc


@scope_group.command("remove")
@click.argument("key")
@click.argument("scope")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def remove_cmd(key: str, scope: str, vault_path: str) -> None:
    """Remove KEY from SCOPE."""
    removed = remove_scope(vault_path, key, scope)
    if removed:
        click.echo(f"Removed '{key}' from scope '{scope}'.")
    else:
        click.echo(f"'{key}' was not in scope '{scope}'.")


@scope_group.command("list")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def list_cmd(vault_path: str) -> None:
    """List all scopes in use."""
    scopes = list_scopes(vault_path)
    if not scopes:
        click.echo("No scopes defined.")
    else:
        for s in scopes:
            click.echo(s)


@scope_group.command("show")
@click.argument("scope")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def show_cmd(scope: str, vault_path: str) -> None:
    """Show all keys assigned to SCOPE."""
    keys = keys_in_scope(vault_path, scope)
    if not keys:
        click.echo(f"No keys in scope '{scope}'.")
    else:
        for k in keys:
            click.echo(k)


@scope_group.command("clear")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def clear_cmd(key: str, vault_path: str) -> None:
    """Remove all scope assignments for KEY."""
    clear_scopes(vault_path, key)
    click.echo(f"Cleared all scopes for '{key}'.")


@scope_group.command("get")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.json", show_default=True)
def get_cmd(key: str, vault_path: str) -> None:
    """Show all scopes assigned to KEY."""
    scopes = get_scopes(vault_path, key)
    if not scopes:
        click.echo(f"No scopes assigned to '{key}'.")
    else:
        for s in scopes:
            click.echo(s)
