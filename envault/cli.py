"""CLI entry-point for envault."""

import click

from envault.config import init_config, load_config
from envault.vault import get_vault_path, seal, unseal


@click.group()
def cli():
    """envault — encrypt and manage .env files."""


@cli.command()
@click.option(
    "--vault-dir",
    default=".envault",
    show_default=True,
    help="Directory to store encrypted vaults.",
)
@click.option(
    "--env-file",
    default=".env",
    show_default=True,
    help="Default .env file to manage.",
)
def init(vault_dir, env_file):
    """Initialise envault for the current project."""
    config = init_config(vault_dir=vault_dir, default_env_file=env_file)
    click.echo(f"Initialised envault (vault_dir={config['vault_dir']}, env={config['default_env_file']})")


@cli.command()
@click.argument("env_file", default=None, required=False)
@click.password_option(prompt="Encryption password")
def lock(env_file, password):
    """Encrypt ENV_FILE and store it in the vault."""
    config = load_config()
    target = env_file or config["default_env_file"]
    vault_path = get_vault_path(target, vault_dir=config["vault_dir"])
    seal(target, password, vault_dir=config["vault_dir"])
    click.echo(f"Locked '{target}' -> '{vault_path}'")


@cli.command()
@click.argument("env_file", default=None, required=False)
@click.option("--password", prompt=True, hide_input=True, help="Decryption password.")
def unlock(env_file, password):
    """Decrypt a vault entry back to ENV_FILE."""
    config = load_config()
    target = env_file or config["default_env_file"]
    unseal(target, password, vault_dir=config["vault_dir"])
    click.echo(f"Unlocked vault -> '{target}'")
