"""
Enhanced Management Framework

Unified command management framework with a flexible command registry,
comprehensive CLI integration, and support for backward compatibility.
"""

from .command_registry import CommandRegistry, register
from .cli_integration import execute_from_command_line

# Import commands to register them
from .commands import project_commands

# Import AgentStudioCLI from cli module
try:
    from ..cli.main import AgentStudioCLI
except ImportError:
    AgentStudioCLI = None

__all__ = [
    "CommandRegistry",
    "register",
    "AgentStudioCLI",
    "execute_from_command_line",
]
