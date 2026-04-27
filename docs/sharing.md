# Secure Secret Sharing

envault supports sharing a subset (or all) of your vault's secrets with teammates or across environments using **encrypted bundles**.

A bundle is a single, self-contained, base64-encoded string that can be transmitted safely over any channel (Slack, email, CI variable, etc.).

---

## Creating a bundle

```bash
# Share all secrets
envault share create --vault-path .envault

# Share specific keys only
envault share create --vault-path .envault --key DB_HOST --key API_KEY

# Bundle that expires in 1 hour (3600 seconds)
envault share create --vault-path .envault --expires-in 3600
```

You will be prompted for:
1. **Vault password** — the password that unlocks your local vault.
2. **Share password** — a *separate* password used to encrypt the bundle. Share this with the recipient through a secure channel.

The command outputs a single encoded string, e.g.:
```
eyJzYWx0IjogIi4uLiIsICJ0b2tlbiI6ICIuLi4ifQ==
```

---

## Importing a bundle

```bash
envault share import <BUNDLE_STRING> --vault-path .envault
```

You will be prompted for the vault password and the share password. Imported keys are merged into the destination vault.

---

## Security model

| Property | Detail |
|---|---|
| Encryption | AES-256-GCM via `cryptography` Fernet (same as vault) |
| Key derivation | PBKDF2-HMAC-SHA256 with a random 16-byte salt per bundle |
| Vault password isolation | The share password is **independent** of the vault password |
| Expiry | Optional TTL checked on import; expired bundles are rejected |

> **Tip:** Never reuse the vault master password as the share password.
