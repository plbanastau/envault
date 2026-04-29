"""Notification hooks for vault events (set, delete, rotate, etc.)."""

import json
import smtplib
import urllib.request
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

NOTIFY_FILE = ".envault_notify.json"

VALID_CHANNELS = ("webhook", "email")


class NotificationError(Exception):
    pass


def _notify_path(vault_path: str) -> Path:
    return Path(vault_path).parent / NOTIFY_FILE


def _load(vault_path: str) -> dict:
    p = _notify_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _notify_path(vault_path).write_text(json.dumps(data, indent=2))


def configure(vault_path: str, channel: str, **kwargs) -> None:
    """Configure a notification channel for the vault."""
    if channel not in VALID_CHANNELS:
        raise NotificationError(
            f"Unknown channel '{channel}'. Valid: {VALID_CHANNELS}"
        )
    data = _load(vault_path)
    data[channel] = kwargs
    _save(vault_path, data)


def get_config(vault_path: str, channel: str) -> Optional[dict]:
    """Return config for a channel, or None if not configured."""
    return _load(vault_path).get(channel)


def remove_channel(vault_path: str, channel: str) -> bool:
    """Remove a notification channel. Returns True if it existed."""
    data = _load(vault_path)
    if channel not in data:
        return False
    del data[channel]
    _save(vault_path, data)
    return True


def notify(vault_path: str, event: str, detail: str = "") -> list[str]:
    """Fire notifications for an event. Returns list of channels notified."""
    data = _load(vault_path)
    notified = []

    if "webhook" in data:
        cfg = data["webhook"]
        url = cfg.get("url", "")
        if url:
            payload = json.dumps({"event": event, "detail": detail}).encode()
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=5)
                notified.append("webhook")
            except Exception as exc:
                raise NotificationError(f"Webhook delivery failed: {exc}") from exc

    if "email" in data:
        cfg = data["email"]
        try:
            msg = MIMEText(f"Event: {event}\nDetail: {detail}")
            msg["Subject"] = f"[envault] {event}"
            msg["From"] = cfg["from"]
            msg["To"] = cfg["to"]
            with smtplib.SMTP(cfg.get("host", "localhost"), cfg.get("port", 25)) as s:
                s.sendmail(cfg["from"], [cfg["to"]], msg.as_string())
            notified.append("email")
        except Exception as exc:
            raise NotificationError(f"Email delivery failed: {exc}") from exc

    return notified
