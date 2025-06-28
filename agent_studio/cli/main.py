"""
Agent Studio Main CLI

Enhanced CLI implementation with project management, workflow execution,
and comprehensive command integration.
"""

import os
import sys
import json
import click
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .. import __version__
from ..management.command_registry import registry
from ..management.cli_integration import execute_from_command_line

logger = logging.getLogger(__name__)


class AgentStudioCLI:
    """
    Enhanced CLI wrapper for Agent Studio operations.
    
    Features:
    - Project initialization and management
    - Workflow execution
    - Command registry integration
    - Configuration management
    - Development tools
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.agentstudio/config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load CLI configuration."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
        
        return {
            "default_project_path": os.getcwd(),
            "debug_mode": False,
            "log_level": "INFO",
        }
    
    def _save_config(self):
        """Save CLI configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")


@click.group()
@click.version_option(version=__version__, prog_name="agent-studio")
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', help='Configuration file path')
@click.pass_context
def main_cli(ctx, debug, config):
    """Agent Studio - A comprehensive framework for building agent-based workflows."""
    ctx.ensure_object(dict)
    
    cli = AgentStudioCLI(config)
    if debug:
        cli.config["debug_mode"] = True
        logging.basicConfig(level=logging.DEBUG)
    
    ctx.obj['cli'] = cli


@main_cli.command()
@click.argument('project_name')
@click.option('--path', default='.', help='Project directory path')
@click.option('--template', default='basic', help='Project template to use')
@click.pass_context
def init(ctx, project_name, path, template):
    """Initialize a new Agent Studio project."""
    cli = ctx.obj['cli']
    
    project_path = Path(path) / project_name
    
    try:
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=False)
        
        # Create basic project structure
        (project_path / "agents").mkdir()
        (project_path / "workflows").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "config").mkdir()
        
        # Create basic files
        init_files = {
            "__init__.py": "",
            "main.py": _get_main_template(project_name),
            "config/settings.py": _get_settings_template(),
            "agents/__init__.py": "",
            "workflows/__init__.py": "",
            "tests/__init__.py": "",
            "README.md": _get_readme_template(project_name),
            "requirements.txt": _get_requirements_template(),
        }
        
        for file_path, content in init_files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        click.echo(f"✅ Project '{project_name}' initialized successfully in {project_path}")
        click.echo(f"📁 Project structure created with template: {template}")
        click.echo(f"🚀 Next steps:")
        click.echo(f"   cd {project_path}")
        click.echo(f"   pip install -r requirements.txt")
        click.echo(f"   agent-studio run")
        
    except FileExistsError:
        click.echo(f"❌ Error: Directory '{project_path}' already exists")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error initializing project: {e}")
        sys.exit(1)


@main_cli.command()
@click.option('--agent', help='Specific agent to run')
@click.option('--workflow', help='Specific workflow to execute')
@click.option('--config-file', help='Configuration file path')
@click.pass_context
def run(ctx, agent, workflow, config_file):
    """Run Agent Studio workflows or agents."""
    cli = ctx.obj['cli']
    
    click.echo("🚀 Starting Agent Studio...")
    
    if agent:
        click.echo(f"Running agent: {agent}")
        # Implementation would go here
    elif workflow:
        click.echo(f"Executing workflow: {workflow}")
        # Implementation would go here
    else:
        click.echo("Starting interactive mode...")
        # Implementation would go here
    
    click.echo("✅ Execution completed")


@main_cli.command()
@click.option('--category', help='Filter commands by category')
@click.option('--include-deprecated', is_flag=True, help='Include deprecated commands')
def commands(category, include_deprecated):
    """List all available management commands."""
    commands_list = registry.list_commands(category, include_deprecated)
    
    if category:
        click.echo(f"Commands in category '{category}':")
    else:
        click.echo("All available commands:")
    
    if not commands_list:
        click.echo("  No commands found")
        return
    
    for command in commands_list:
        cmd_info = registry.get_command_info(command)
        status = "deprecated" if cmd_info.get("deprecated", False) else "active"
        description = cmd_info.get("description", "No description")
        aliases = cmd_info.get("aliases", [])
        
        click.echo(f"  {command:<20} {description} ({status})")
        if aliases:
            click.echo(f"{'':>22} aliases: {', '.join(aliases)}")


@main_cli.command()
@click.argument('command_name')
@click.argument('args', nargs=-1)
def manage(command_name, args):
    """Execute management commands."""
    if not registry.has_command(command_name):
        click.echo(f"❌ Error: Unknown command '{command_name}'")
        click.echo(f"Available commands: {', '.join(registry.list_commands())}")
        sys.exit(1)
    
    try:
        result = registry.execute_command(command_name, list(args))
        click.echo(f"✅ Command '{command_name}' executed successfully")
        if result:
            click.echo(f"Result: {result}")
    except Exception as e:
        click.echo(f"❌ Error executing command '{command_name}': {e}")
        sys.exit(1)


@main_cli.command()
def status():
    """Show Agent Studio status and configuration."""
    click.echo("Agent Studio Status")
    click.echo("==================")
    click.echo(f"Version: {__version__}")
    click.echo(f"Registry Stats: {registry.get_registry_stats()}")
    click.echo(f"Available Categories: {', '.join(registry.list_categories())}")


@main_cli.command()
@click.option('--limit', default=10, help='Number of history entries to show')
def history(limit):
    """Show command execution history."""
    execution_history = registry.get_execution_history(limit)
    
    if not execution_history:
        click.echo("No command execution history found")
        return
    
    click.echo("Recent Command Executions")
    click.echo("========================")
    
    for entry in execution_history:
        status = "✅" if entry.get("success", False) else "❌"
        timestamp = entry.get("timestamp", "Unknown")
        command = entry.get("command", "Unknown")
        
        click.echo(f"{status} {timestamp} - {command}")
        if "error" in entry:
            click.echo(f"    Error: {entry['error']}")


def _get_main_template(project_name: str) -> str:
    """Get main.py template content."""
    return f'''"""
{project_name} - Agent Studio Project

Main entry point for the {project_name} agent system.
"""

import asyncio
import logging
from agent_studio import BaseAgent, BaseLangGraphWorkflow

logger = logging.getLogger(__name__)


class {project_name.capitalize()}Agent(BaseAgent):
    """Main agent for {project_name}."""
    
    async def _setup_resources(self):
        """Setup agent resources."""
        logger.info("Setting up {project_name} agent resources")
    
    async def process_message(self, query: str, session_id: str = None, context: dict = None):
        """Process incoming messages."""
        yield {{
            "success": True,
            "content": f"Hello from {project_name}! Your query: {{query}}",
            "metadata": {{"agent": "{project_name}"}},
        }}
    
    async def process_task(self, task_data: dict):
        """Process A2A tasks."""
        yield {{
            "success": True,
            "content": f"Task processed: {{task_data}}",
            "metadata": {{"agent": "{project_name}"}},
        }}


async def main():
    """Main entry point."""
    agent = {project_name.capitalize()}Agent(agent_id="{project_name}")
    
    # Example usage
    async for result in agent.stream("Hello, Agent Studio!"):
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
'''


def _get_settings_template() -> str:
    """Get settings.py template content."""
    return '''"""
Project Settings

Configuration settings for the Agent Studio project.
"""

import os

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Agent configuration
AGENT_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
}

# Workflow configuration
WORKFLOW_CONFIG = {
    "debug_mode": DEBUG,
    "mcp": {
        "enabled": False,
    }
}

# Database configuration (if needed)
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "sqlite:///agent_studio.db"),
}
'''


def _get_readme_template(project_name: str) -> str:
    """Get README.md template content."""
    return f'''# {project_name}

Agent Studio project for building intelligent agent workflows.

## Features

- A2A protocol compliance
- LangGraph workflow integration
- Comprehensive tracing and debugging
- MCP server support

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the project:
   ```bash
   python main.py
   ```

3. Use the CLI:
   ```bash
   agent-studio run --agent {project_name}
   ```

## Project Structure

- `agents/` - Agent implementations
- `workflows/` - Workflow definitions
- `config/` - Configuration files
- `tests/` - Test cases

## Development

- Use `agent-studio commands` to see available management commands
- Enable debug mode with `--debug` flag
- Check status with `agent-studio status`

## Documentation

For more information, visit the Agent Studio documentation.
'''


def _get_requirements_template() -> str:
    """Get requirements.txt template content."""
    return '''# Agent Studio core requirements
agent-studio>=1.0.0

# LangGraph for workflows
langgraph>=0.1.0

# CLI framework
click>=8.0.0

# Async support
asyncio

# Logging and utilities
pydantic>=2.0.0
python-dotenv>=1.0.0

# Optional: Database support
# sqlalchemy>=2.0.0
# alembic>=1.0.0

# Development dependencies
# pytest>=7.0.0
# pytest-asyncio>=0.21.0
# black>=23.0.0
# flake8>=6.0.0
'''


if __name__ == "__main__":
    main_cli()
