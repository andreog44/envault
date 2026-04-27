"""CLI entry point for envault."""

import sys
import click
from envault.vault import seal, unseal


@click.group()
@click.version_option(package_name="envault")
def cli():
    """envault — Encrypt and manage environment variable files."""


@cli.command()
@click.argument("env_file", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output vault file path.")
@click.password_option("-p", "--password", help="Encryption password.")
def lock(env_file, output, password):
    """Encrypt ENV_FILE into a .vault file."""
    try:
        vault_path = seal(env_file, password, output_path=output)
        click.secho(f"✔ Sealed: {vault_path}", fg="green")
    except Exception as exc:
        click.secho(f"✖ Error: {exc}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("vault_file", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output env file path.")
@click.option("-p", "--password", prompt=True, hide_input=True, help="Decryption password.")
def unlock(vault_file, output, password):
    """Decrypt VAULT_FILE back into a plaintext .env file."""
    try:
        env_path = unseal(vault_file, password, output_path=output)
        click.secho(f"✔ Unsealed: {env_path}", fg="green")
    except ValueError as exc:
        click.secho(f"✖ {exc}", fg="red", err=True)
        sys.exit(1)
    except Exception as exc:
        click.secho(f"✖ Error: {exc}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
