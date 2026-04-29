"""CLI commands for password rotation."""

import click
from pathlib import Path
from envault.rotate import rotate_password, backup_vault


@click.group(name="rotate")
def rotate_group():
    """Rotate the encryption password for a vault."""


@rotate_group.command(name="password")
@click.option(
    "--profile",
    default="default",
    show_default=True,
    help="Profile whose vault password should be rotated.",
)
@click.option(
    "--backup/--no-backup",
    default=True,
    show_default=True,
    help="Create a timestamped backup before rotating.",
)
@click.option(
    "--project-dir",
    default=".",
    show_default=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Project root directory.",
)
def password_cmd(profile: str, backup: bool, project_dir: Path):
    """Re-encrypt the vault with a new password."""
    old_password = click.prompt(
        "Current password", hide_input=True, confirmation_prompt=False
    )
    new_password = click.prompt(
        "New password", hide_input=True, confirmation_prompt=True
    )

    if backup:
        try:
            bak = backup_vault(project_dir, profile)
            click.echo(f"Backup created: {bak}")
        except FileNotFoundError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1)

    try:
        vault_path = rotate_password(project_dir, old_password, new_password, profile)
        click.echo(f"Password rotated successfully for vault: {vault_path}")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
