"""CLI commands for key labeling."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.labeling import LabelingError, get_label, keys_with_label, list_labels, remove_label, set_label


@click.group("label", help="Attach human-readable labels to secret keys.")
def label_group() -> None:  # pragma: no cover
    pass


@label_group.command("set")
@click.argument("key")
@click.argument("label")
@click.option("--vault", "vault_path", default="vault.enc", show_default=True)
def set_cmd(key: str, label: str, vault_path: str) -> None:
    """Set a display LABEL for KEY."""
    try:
        stored = set_label(vault_path, key, label)
        click.echo(f"Label set: {key!r} \u2192 {stored!r}")
    except LabelingError as exc:
        raise click.ClickException(str(exc)) from exc


@label_group.command("get")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.enc", show_default=True)
def get_cmd(key: str, vault_path: str) -> None:
    """Print the label for KEY."""
    lbl = get_label(vault_path, key)
    if lbl is None:
        click.echo(f"No label set for {key!r}.")
    else:
        click.echo(lbl)


@label_group.command("remove")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.enc", show_default=True)
def remove_cmd(key: str, vault_path: str) -> None:
    """Remove the label for KEY."""
    removed = remove_label(vault_path, key)
    if removed:
        click.echo(f"Label removed for {key!r}.")
    else:
        click.echo(f"No label found for {key!r}.")


@label_group.command("list")
@click.option("--vault", "vault_path", default="vault.enc", show_default=True)
@click.option("--sort", "sort_by", type=click.Choice(["key", "label"]), default="key", show_default=True, help="Sort output by key or label.")
def list_cmd(vault_path: str, sort_by: str) -> None:
    """List all key labels, optionally sorted by KEY or LABEL."""
    entries = list_labels(vault_path)
    if not entries:
        click.echo("No labels defined.")
        return
    sorted_entries = sorted(entries, key=lambda e: e[sort_by].lower())
    for entry in sorted_entries:
        click.echo(f"{entry['key']:<30} {entry['label']}")


@label_group.command("find")
@click.argument("label")
@click.option("--vault", "vault_path", default="vault.enc", show_default=True)
def find_cmd(label: str, vault_path: str) -> None:
    """Find all keys with a given LABEL."""
    keys = keys_with_label(vault_path, label)
    if not keys:
        click.echo(f"No keys with label {label!r}.")
        return
    for key in keys:
        click.echo(key)
