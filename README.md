# envault

> A CLI tool for managing and encrypting environment variable files across multiple projects.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install envault
```

---

## Usage

```bash
# Encrypt a .env file
envault encrypt .env --output .env.vault

# Decrypt a vault file
envault decrypt .env.vault --output .env

# Push encrypted env to a named project
envault push myproject --env production

# Pull and decrypt env for a project
envault pull myproject --env production
```

Secrets are encrypted using AES-256-GCM. A master key is generated on first use and stored in `~/.envault/keystore`.

---

## Why envault?

- 🔐 **Encrypted at rest** — never commit plaintext secrets again
- 📁 **Multi-project support** — manage `.env` files across all your projects from one place
- ⚡ **Simple CLI** — intuitive commands with minimal configuration
- 🔑 **Key management** — rotate keys and re-encrypt with a single command

---

## Requirements

- Python 3.8+
- `cryptography` >= 41.0

---

## License

MIT © [envault contributors](https://github.com/yourname/envault)