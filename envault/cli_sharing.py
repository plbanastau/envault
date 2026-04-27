"""CLI commands for sharing vault secrets via encrypted bundles."""

import click

from envault.cli import get_vault
from envault.sharing import create_bundle, import_bundle, SharingError


@click.group("share")
def share_group():
    """Commands for sharing secrets securely."""


@share_group.command("create")
@click.option("--vault-path", default=".envault", show_default=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--share-password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password to protect the bundle.")
@click.option("--key", "keys", multiple=True, default=None, help="Keys to include (repeatable). Omit for all.")
@click.option("--expires-in", default=None, type=int, help="Bundle TTL in seconds.")
def create_cmd(vault_path, password, share_password, keys, expires_in):
    """Create an encrypted sharing bundle."""
    vault = get_vault(vault_path, password)
    try:
        bundle = create_bundle(
            vault,
            share_password,
            keys=list(keys) if keys else None,
            expires_in=expires_in,
        )
    except SharingError as exc:
        raise click.ClickException(str(exc))

    click.echo(bundle)


@share_group.command("import")
@click.argument("bundle")
@click.option("--vault-path", default=".envault", show_default=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--share-password", prompt=True, hide_input=True, help="Password protecting the bundle.")
def import_cmd(bundle, vault_path, password, share_password):
    """Import secrets from an encrypted sharing bundle."""
    vault = get_vault(vault_path, password)
    try:
        imported = import_bundle(vault, bundle, share_password)
    except SharingError as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Imported {len(imported)} key(s): {', '.join(sorted(imported))}")
