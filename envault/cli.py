"""CLI entry point for envault."""

import click
from envault.vault import Vault
from envault import audit

DEFAULT_VAULT = ".envault"


def get_vault(vault_path: str, password: str) -> Vault:
    v = Vault(vault_path)
    v.load(password)
    return v


@click.group()
def cli():
    """envault — encrypted environment variable manager."""


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option()
def set(key, value, vault, password):
    """Set a secret KEY to VALUE."""
    v = get_vault(vault, password)
    v.set(key, value)
    v.save(password)
    audit.record(vault, "set", key)
    click.echo(f"✓ Set {key}")


@cli.command()
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Password", confirmation_prompt=False)
def get(key, vault, password):
    """Get the value of KEY."""
    v = get_vault(vault, password)
    value = v.get(key)
    audit.record(vault, "get", key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    else:
        click.echo(value)


@cli.command(name="list")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Password", confirmation_prompt=False)
def list_keys(vault, password):
    """List all keys in the vault."""
    v = get_vault(vault, password)
    keys = v.keys()
    if not keys:
        click.echo("(empty vault)")
    for k in sorted(keys):
        click.echo(k)


@cli.command()
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Password", confirmation_prompt=False)
def delete(key, vault, password):
    """Delete KEY from the vault."""
    v = get_vault(vault, password)
    removed = v.delete(key)
    if removed:
        v.save(password)
        audit.record(vault, "delete", key)
        click.echo(f"✓ Deleted {key}")
    else:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)


@cli.command(name="audit-log")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.option("--tail", default=0, help="Show only the last N entries (0 = all).")
def audit_log(vault, tail):
    """Show the audit log for the vault."""
    entries = audit.get_log(vault)
    if not entries:
        click.echo("No audit entries found.")
        return
    if tail > 0:
        entries = entries[-tail:]
    for entry in entries:
        click.echo(
            f"{entry['timestamp']}  {entry['actor']:12s}  {entry['action']:8s}  {entry['key']}"
        )


if __name__ == "__main__":
    cli()
