"""CLI commands for secret group management."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.grouping import (
    GroupingError,
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    delete_group,
    groups_for_key,
)


@click.group("group")
def group_group() -> None:
    """Manage secret groups."""


@group_group.command("add")
@click.argument("group")
@click.argument("key")
@click.pass_context
def add_cmd(ctx: click.Context, group: str, key: str) -> None:
    """Add KEY to GROUP."""
    vault_path = get_vault(ctx)
    try:
        add_to_group(vault_path, group, key)
        click.echo(f"Added '{key}' to group '{group}'.")
    except GroupingError as exc:
        raise click.ClickException(str(exc)) from exc


@group_group.command("remove")
@click.argument("group")
@click.argument("key")
@click.pass_context
def remove_cmd(ctx: click.Context, group: str, key: str) -> None:
    """Remove KEY from GROUP."""
    vault_path = get_vault(ctx)
    removed = remove_from_group(vault_path, group, key)
    if removed:
        click.echo(f"Removed '{key}' from group '{group}'.")
    else:
        click.echo(f"Key '{key}' not found in group '{group}'.")


@group_group.command("list")
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    """List all groups."""
    vault_path = get_vault(ctx)
    groups = list_groups(vault_path)
    if not groups:
        click.echo("No groups defined.")
        return
    for g in groups:
        click.echo(g)


@group_group.command("show")
@click.argument("group")
@click.pass_context
def show_cmd(ctx: click.Context, group: str) -> None:
    """Show all keys in GROUP."""
    vault_path = get_vault(ctx)
    members = get_group(vault_path, group)
    if not members:
        click.echo(f"Group '{group}' is empty or does not exist.")
        return
    for key in members:
        click.echo(key)


@group_group.command("delete")
@click.argument("group")
@click.pass_context
def delete_cmd(ctx: click.Context, group: str) -> None:
    """Delete GROUP entirely."""
    vault_path = get_vault(ctx)
    deleted = delete_group(vault_path, group)
    if deleted:
        click.echo(f"Deleted group '{group}'.")
    else:
        click.echo(f"Group '{group}' not found.")


@group_group.command("of")
@click.argument("key")
@click.pass_context
def of_cmd(ctx: click.Context, key: str) -> None:
    """List all groups that contain KEY."""
    vault_path = get_vault(ctx)
    groups = groups_for_key(vault_path, key)
    if not groups:
        click.echo(f"Key '{key}' is not in any group.")
        return
    for g in groups:
        click.echo(g)
