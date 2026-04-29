"""CLI commands for viewing and managing the audit log."""

import click
from pathlib import Path

from envault.audit import load_audit_log, clear_audit_log, get_audit_path


@click.group(name="audit")
def audit_group():
    """View and manage the vault audit log."""


@audit_group.command(name="log")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
@click.option("--limit", default=20, show_default=True, help="Max entries to display.")
def log_cmd(project_dir: str, limit: int):
    """Display recent audit log entries."""
    entries = load_audit_log(project_dir)
    if not entries:
        click.echo("No audit log entries found.")
        return
    recent = entries[-limit:]
    for entry in reversed(recent):
        profile_info = f" [{entry['profile']}]" if entry.get("profile") else ""
        details_info = f" — {entry['details']}" if entry.get("details") else ""
        click.echo(
            f"{entry['timestamp']}  {entry['user']:12s}  {entry['action']}{profile_info}{details_info}"
        )


@audit_group.command(name="clear")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_cmd(project_dir: str):
    """Clear all audit log entries."""
    clear_audit_log(project_dir)
    click.echo("Audit log cleared.")


@audit_group.command(name="path")
@click.option("--project-dir", default=".", show_default=True, help="Project directory.")
def path_cmd(project_dir: str):
    """Print the path to the audit log file."""
    click.echo(str(get_audit_path(project_dir)))
