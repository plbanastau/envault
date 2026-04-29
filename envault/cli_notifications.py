"""CLI commands for managing vault notifications."""

import click
from envault.cli import get_vault
from envault.notifications import configure, get_config, remove_channel, NotificationError


@click.group(name="notify")
def notify_group():
    """Manage vault event notifications."""


@notify_group.command("webhook")
@click.argument("vault_path")
@click.argument("url")
def webhook_cmd(vault_path, url):
    """Configure a webhook notification channel."""
    try:
        configure(vault_path, "webhook", url=url)
        click.echo(f"Webhook configured: {url}")
    except NotificationError as exc:
        raise click.ClickException(str(exc))


@notify_group.command("email")
@click.argument("vault_path")
@click.option("--host", default="localhost", show_default=True, help="SMTP host")
@click.option("--port", default=25, show_default=True, help="SMTP port")
@click.option("--from", "from_addr", required=True, help="Sender address")
@click.option("--to", "to_addr", required=True, help="Recipient address")
def email_cmd(vault_path, host, port, from_addr, to_addr):
    """Configure an email notification channel."""
    try:
        configure(
            vault_path, "email",
            host=host, port=port,
            **{"from": from_addr, "to": to_addr},
        )
        click.echo(f"Email notifications configured ({from_addr} -> {to_addr})")
    except NotificationError as exc:
        raise click.ClickException(str(exc))


@notify_group.command("show")
@click.argument("vault_path")
@click.argument("channel")
def show_cmd(vault_path, channel):
    """Show configuration for a notification channel."""
    cfg = get_config(vault_path, channel)
    if cfg is None:
        click.echo(f"No configuration found for channel '{channel}'.")
    else:
        for key, value in cfg.items():
            click.echo(f"  {key}: {value}")


@notify_group.command("remove")
@click.argument("vault_path")
@click.argument("channel")
def remove_cmd(vault_path, channel):
    """Remove a notification channel."""
    removed = remove_channel(vault_path, channel)
    if removed:
        click.echo(f"Channel '{channel}' removed.")
    else:
        click.echo(f"Channel '{channel}' was not configured.")
