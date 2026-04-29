"""Tests for envault/notifications.py."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.notifications import (
    configure,
    get_config,
    remove_channel,
    notify,
    NotificationError,
    _notify_path,
)


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_configure_webhook(vault_path):
    configure(vault_path, "webhook", url="https://example.com/hook")
    cfg = get_config(vault_path, "webhook")
    assert cfg["url"] == "https://example.com/hook"


def test_configure_email(vault_path):
    configure(vault_path, "email", host="smtp.example.com", port=587,
              from_="a@example.com", to="b@example.com")
    cfg = get_config(vault_path, "email")
    assert cfg["host"] == "smtp.example.com"
    assert cfg["port"] == 587


def test_configure_invalid_channel_raises(vault_path):
    with pytest.raises(NotificationError, match="Unknown channel"):
        configure(vault_path, "slack", token="xxx")


def test_get_config_missing_channel_returns_none(vault_path):
    assert get_config(vault_path, "webhook") is None


def test_remove_channel_returns_true_when_exists(vault_path):
    configure(vault_path, "webhook", url="https://example.com/hook")
    assert remove_channel(vault_path, "webhook") is True
    assert get_config(vault_path, "webhook") is None


def test_remove_channel_returns_false_when_missing(vault_path):
    assert remove_channel(vault_path, "webhook") is False


def test_notify_webhook_called(vault_path):
    configure(vault_path, "webhook", url="https://example.com/hook")
    mock_response = MagicMock()
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
        channels = notify(vault_path, "set", detail="MY_KEY")
    assert "webhook" in channels
    mock_open.assert_called_once()


def test_notify_webhook_failure_raises(vault_path):
    configure(vault_path, "webhook", url="https://example.com/hook")
    with patch("urllib.request.urlopen", side_effect=OSError("timeout")):
        with pytest.raises(NotificationError, match="Webhook delivery failed"):
            notify(vault_path, "set", detail="KEY")


def test_notify_no_channels_returns_empty(vault_path):
    channels = notify(vault_path, "set", detail="KEY")
    assert channels == []


def test_notify_file_persists_multiple_channels(vault_path):
    configure(vault_path, "webhook", url="https://example.com/hook")
    configure(vault_path, "email", host="smtp.example.com", port=25,
              **{"from": "a@x.com", "to": "b@x.com"})
    p = _notify_path(vault_path)
    data = json.loads(p.read_text())
    assert "webhook" in data
    assert "email" in data


def test_configure_overwrites_existing(vault_path):
    configure(vault_path, "webhook", url="https://old.example.com")
    configure(vault_path, "webhook", url="https://new.example.com")
    cfg = get_config(vault_path, "webhook")
    assert cfg["url"] == "https://new.example.com"
