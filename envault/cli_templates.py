"""CLI commands for managing vault templates."""
from __future__ import annotations

import click

from envault.cli import get_vault
from envault.templates import (
    TemplateError,
    apply_template,
    delete_template,
    get_template,
    list_templates,
    save_template,
)


@click.group("template")
def template_group():
    """Manage key templates for scaffolding environments."""


@template_group.command("save")
@click.argument("name")
@click.argument("keypairs", nargs=-1, metavar="KEY=DEFAULT ...")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def save_cmd(name: str, keypairs: tuple, vault_path: str):
    """Save a template with KEY=DEFAULT pairs."""
    keys: dict[str, str] = {}
    for pair in keypairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair}")
        k, _, v = pair.partition("=")
        keys[k.strip()] = v.strip()
    try:
        save_template(vault_path, name, keys)
        click.echo(f"Template '{name}' saved with {len(keys)} key(s).")
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc


@template_group.command("list")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def list_cmd(vault_path: str):
    """List all saved templates."""
    names = list_templates(vault_path)
    if not names:
        click.echo("No templates defined.")
    for name in names:
        click.echo(name)


@template_group.command("show")
@click.argument("name")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def show_cmd(name: str, vault_path: str):
    """Show keys and defaults for a template."""
    try:
        tmpl = get_template(vault_path, name)
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc
    for key, default in sorted(tmpl.items()):
        click.echo(f"{key}={default}")


@template_group.command("delete")
@click.argument("name")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
def delete_cmd(name: str, vault_path: str):
    """Delete a template."""
    if delete_template(vault_path, name):
        click.echo(f"Template '{name}' deleted.")
    else:
        raise click.ClickException(f"Template '{name}' not found.")


@template_group.command("apply")
@click.argument("name")
@click.option("--vault", "vault_path", envvar="ENVAULT_VAULT", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def apply_cmd(name: str, vault_path: str, password: str, overwrite: bool):
    """Apply a template to the vault, filling in default values."""
    try:
        written = apply_template(vault_path, name, password, overwrite=overwrite)
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc
    if written:
        click.echo(f"Applied {len(written)} key(s): {', '.join(sorted(written))}")
    else:
        click.echo("No keys written (all already present; use --overwrite to force).")
