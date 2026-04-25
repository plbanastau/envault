# envault

> A CLI tool for managing and encrypting environment variables across multiple projects and environments.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

```bash
# Initialize a new vault for your project
envault init my-project

# Add an encrypted environment variable
envault set my-project DATABASE_URL "postgres://user:pass@localhost/db"

# Retrieve a variable
envault get my-project DATABASE_URL

# Export all variables for an environment
envault export my-project --env production > .env

# List all stored keys
envault list my-project
```

Envault stores encrypted secrets locally in `~/.envault/` using AES-256 encryption. Each project can have multiple named environments (e.g. `development`, `staging`, `production`).

---

## Configuration

Set a master password via environment variable to avoid interactive prompts:

```bash
export ENVAULT_MASTER_PASSWORD="your-secure-password"
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Contributions and issues welcome — please open a GitHub issue to get started.*