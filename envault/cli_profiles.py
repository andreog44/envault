"""CLI commands for managing envault profiles."""

import click
from pathlib import Path

from envault.profiles import (
    list_profiles,
    add_profile,
    remove_profile,
    set_active_profile,
    get_active_profile,
)


@click.group("profile")
def profile_group():
    """Manage named environment profiles for this project."""


@profile_group.command("list")
@click.option("--dir", "project_dir", default=".", show_default=True, help="Project directory.")
def list_cmd(project_dir):
    """List all profiles for the current project."""
    path = Path(project_dir)
    profiles = list_profiles(path)
    active = get_active_profile(path)
    if not profiles:
        click.echo("No profiles found. Run 'envault profile add' to create one.")
        return
    for name in profiles:
        marker = " (active)" if name == active else ""
        click.echo(f"  {name}{marker}")


@profile_group.command("add")
@click.argument("name")
@click.option("--env-file", default=".env", show_default=True, help="Path to the .env file for this profile.")
@click.option("--dir", "project_dir", default=".", show_default=True, help="Project directory.")
def add_cmd(name, env_file, project_dir):
    """Add a new profile NAME with the specified env file."""
    path = Path(project_dir)
    add_profile(path, name, env_file)
    click.echo(f"Profile '{name}' added (env file: {env_file}).")


@profile_group.command("remove")
@click.argument("name")
@click.option("--dir", "project_dir", default=".", show_default=True, help="Project directory.")
def remove_cmd(name, project_dir):
    """Remove profile NAME from the project."""
    path = Path(project_dir)
    try:
        removed = remove_profile(path, name)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if removed:
        click.echo(f"Profile '{name}' removed.")
    else:
        click.echo(f"Profile '{name}' not found.", err=True)
        raise SystemExit(1)


@profile_group.command("use")
@click.argument("name")
@click.option("--dir", "project_dir", default=".", show_default=True, help="Project directory.")
def use_cmd(name, project_dir):
    """Switch the active profile to NAME."""
    path = Path(project_dir)
    try:
        set_active_profile(path, name)
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(f"Active profile set to '{name}'.")
