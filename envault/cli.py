"""CLI entry point for envault."""

import click
from pathlib import Path

from envault.vault import Vault


DEFAULT_VAULT_PATH = Path(".envault/vault.enc")


def get_vault(vault_path: str, password: str) -> Vault:
    v = Vault(Path(vault_path), password)
    v.load()
    return v


@click.group()
def cli():
    """envault — encrypted environment variable manager."""


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=str(DEFAULT_VAULT_PATH), show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def set(key, value, vault, password):
    """Set an environment variable in the vault."""
    v = get_vault(vault, password)
    v.set(key, value)
    v.save()
    click.echo(f"✔ Set '{key}' in {vault}")


@cli.command()
@click.argument("key")
@click.option("--vault", default=str(DEFAULT_VAULT_PATH), show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def get(key, vault, password):
    """Get an environment variable from the vault."""
    v = get_vault(vault, password)
    value = v.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command(name="list")
@click.option("--vault", default=str(DEFAULT_VAULT_PATH), show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def list_keys(vault, password):
    """List all keys stored in the vault."""
    v = get_vault(vault, password)
    data = v.list_keys()
    if not data:
        click.echo("Vault is empty.")
        return
    for k, val in data.items():
        click.echo(f"{k}={val}")


@cli.command()
@click.argument("key")
@click.option("--vault", default=str(DEFAULT_VAULT_PATH), show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def delete(key, vault, password):
    """Delete a key from the vault."""
    v = get_vault(vault, password)
    removed = v.delete(key)
    if not removed:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    v.save()
    click.echo(f"✔ Deleted '{key}' from {vault}")
