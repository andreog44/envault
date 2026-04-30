"""CLI commands for vault snapshot management."""

import click
from pathlib import Path

from envault.snapshot import (
    list_snapshots,
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
)
from envault.vault import get_vault_path
from envault.config import load_config


def _get_vault_path_from_project(project: str):
    """Load config and resolve vault path from a project directory string."""
    config = load_config(Path(project))
    return get_vault_path(Path(project), config["vault_dir"])


@click.group(name="snapshot")
def snapshot_group():
    """Manage vault snapshots."""


@snapshot_group.command(name="create")
@click.option("--label", "-l", default="", help="Optional label for the snapshot.")
@click.option("--project", "-p", default=".", help="Project directory.", type=click.Path())
def create_cmd(label: str, project: str):
    """Create a snapshot of the current vault."""
    vault_path = _get_vault_path_from_project(project)

    try:
        entry = create_snapshot(vault_path, label=label)
        click.echo(f"Snapshot created: {entry['id']}" + (f" ({label})" if label else ""))
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_group.command(name="list")
@click.option("--project", "-p", default=".", help="Project directory.", type=click.Path())
def list_cmd(project: str):
    """List all snapshots for the current vault."""
    vault_path = _get_vault_path_from_project(project)
    snapshots = list_snapshots(vault_path)

    if not snapshots:
        click.echo("No snapshots found.")
        return

    for s in snapshots:
        label_str = f"  [{s['label']}]" if s.get("label") else ""
        click.echo(f"{s['id']}  {s['timestamp']}{label_str}")


@snapshot_group.command(name="restore")
@click.argument("snapshot_id")
@click.option("--project", "-p", default=".", help="Project directory.", type=click.Path())
def restore_cmd(snapshot_id: str, project: str):
    """Restore the vault from a snapshot."""
    vault_path = _get_vault_path_from_project(project)

    try:
        restore_snapshot(vault_path, snapshot_id)
        click.echo(f"Vault restored from snapshot: {snapshot_id}")
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_group.command(name="delete")
@click.argument("snapshot_id")
@click.option("--project", "-p", default=".", help="Project directory.", type=click.Path())
def delete_cmd(snapshot_id: str, project: str):
    """Delete a snapshot by ID."""
    vault_path = _get_vault_path_from_project(project)

    try:
        delete_snapshot(vault_path, snapshot_id)
        click.echo(f"Snapshot deleted: {snapshot_id}")
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
