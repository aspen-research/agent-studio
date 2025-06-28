"""
CLI Integration for Agent Studio

Enhanced CLI integration with comprehensive command execution,
help system, and backward compatibility.
"""

import sys
import click
from .command_registry import registry

@click.group()
@click.version_option(version="1.0.0", prog_name="AgentStudio")
def agentstudio_cli():
    """AgentStudio - CLI tool for managing agent-based workflows."""
    pass

@agentstudio_cli.command()
@click.argument('command_name')
@click.argument('args', nargs=-1)
def run_command(command_name, args):
    """Run a registered command by name."""
    if not registry.has_command(command_name):
        click.echo(f"Error: Unknown command '{command_name}'")
        click.echo(f"Available commands: {', '.join(registry.list_commands())}")
        sys.exit(1)
    
    try:
        result = registry.execute_command(command_name, *args)
        click.echo(f"Command '{command_name}' executed successfully")
        click.echo(result)
    except Exception as e:
        click.echo(f"Error executing command '{command_name}': {e}")
        sys.exit(1)

@agentstudio_cli.command()
def list_commands():
    """List all available commands."""
    commands = registry.list_commands()
    click.echo("Available commands:")
    for command in commands:
        cmd_info = registry.get_command_info(command)
        click.echo(f"  {command:<20} {cmd_info.get('description', 'No description')} ({'deprecated' if cmd_info.get('deprecated', False) else 'active'})")


def execute_from_command_line(argv=None):
    """Execute command from command line arguments."""
    if argv is None:
        argv = sys.argv

    agentstudio_cli(argv[1:])


if __name__ == "__main__":
    execute_from_command_line()
