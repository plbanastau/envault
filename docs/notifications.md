# Notifications

envault can fire notifications when vault events occur (e.g. `set`, `delete`, `rotate`).

Two channels are supported: **webhook** and **email**.

---

## Configuring a Webhook

```bash
envault notify webhook /path/to/vault.env https://hooks.example.com/envault
```

When an event fires, a `POST` request is sent with a JSON body:

```json
{"event": "set", "detail": "MY_SECRET_KEY"}
```

---

## Configuring Email

```bash
envault notify email /path/to/vault.env \
  --host smtp.example.com \
  --port 587 \
  --from alerts@example.com \
  --to ops@example.com
```

---

## Viewing Channel Config

```bash
envault notify show /path/to/vault.env webhook
```

Output:
```
  url: https://hooks.example.com/envault
```

---

## Removing a Channel

```bash
envault notify remove /path/to/vault.env email
```

---

## Python API

```python
from envault.notifications import configure, notify, remove_channel

# Configure
configure(vault_path, "webhook", url="https://hooks.example.com/envault")

# Fire an event notification manually
notified = notify(vault_path, "rotate", detail="all keys re-encrypted")
print(notified)  # ['webhook']

# Remove a channel
remove_channel(vault_path, "webhook")
```

---

## Errors

`NotificationError` is raised when:
- An unknown channel name is provided.
- A webhook HTTP request fails.
- An SMTP connection or send fails.

All errors include a descriptive message indicating the channel and cause.
