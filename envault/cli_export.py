"""CLI commands for exporting environment variables from vault."""

import click
from pathlib import Path

from envault.config import load_config
from envault.vault import get_vault_path
from envault.export import export_to_shell, export_to_dict


@click.group(name="export")
def export_group():
    """Export environment variables from an encrypted vault."""
    pass


@export_group.command(name="shell")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
@click.option("--profile", default=None, help="Profile name to use.")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
@click.pass_context
def shell_cmd(ctx, vault_dir, profile, password):
    """Print shell export statements for all variables in the vault."""
    project_dir = Path.cwd()
    config = load_config(project_dir)
    resolved_vault_dir = Path(vault_dir) if vault_dir else Path(config.get("vault_dir", ".envault"))
    active_profile = profile or config.get("active_profile", "default")

    vault_path = get_vault_path(resolved_vault_dir, active_profile)
    if not vault_path.exists():
        click.echo(f"Error: No vault found at {vault_path}", err=True)
        ctx.exit(1)
        return

    try:
        output = export_to_shell(vault_path, password)
        click.echo(output)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@export_group.command(name="dotenv")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
@click.option("--profile", default=None, help="Profile name to use.")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout).")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
@click.pass_context
def dotenv_cmd(ctx, vault_dir, profile, output, password):
    """Export vault contents as a .env file."""
    project_dir = Path.cwd()
    config = load_config(project_dir)
    resolved_vault_dir = Path(vault_dir) if vault_dir else Path(config.get("vault_dir", ".envault"))
    active_profile = profile or config.get("active_profile", "default")

    vault_path = get_vault_path(resolved_vault_dir, active_profile)
    if not vault_path.exists():
        click.echo(f"Error: No vault found at {vault_path}", err=True)
        ctx.exit(1)
        return

    try:
        env_vars = export_to_dict(vault_path, password)
        lines = [f'{k}="{v}"' for k, v in env_vars.items()]
        result = "\n".join(lines) + "\n"
        if output:
            Path(output).write_text(result)
            click.echo(f"Exported {len(env_vars)} variable(s) to {output}")
        else:
            click.echo(result, nl=False)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
