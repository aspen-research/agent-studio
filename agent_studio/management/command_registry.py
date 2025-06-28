"""
Enhanced Command Registry

Improved command registry with enhanced features, backward compatibility,
and comprehensive error handling.
"""

import logging
from typing import Dict, Callable, Any, List, Optional
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


class CommandRegistry:
    """
    Enhanced registry for management commands.
    
    Features:
    - Command registration with metadata
    - Backward compatibility support
    - Command categorization
    - Help system integration
    - Performance tracking
    """
    
    def __init__(self):
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._aliases: Dict[str, str] = {}
        self._execution_history: List[Dict[str, Any]] = []
        
    def register(self, 
                 name: str, 
                 category: str = "general",
                 aliases: List[str] = None,
                 description: str = None,
                 deprecated: bool = False):
        """
        Enhanced decorator to register a management command.
        
        Args:
            name: The command name used in CLI
            category: Command category for organization
            aliases: Alternative names for the command
            description: Command description
            deprecated: Whether the command is deprecated
            
        Returns:
            Decorator function that registers the command
        """
        def decorator(func: Callable) -> Callable:
            if name in self._commands:
                logger.warning(f"Command '{name}' is already registered, overriding")
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Track execution
                execution_record = {
                    "command": name,
                    "timestamp": datetime.now().isoformat(),
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }
                
                try:
                    result = func(*args, **kwargs)
                    execution_record["success"] = True
                    return result
                except Exception as e:
                    execution_record["success"] = False
                    execution_record["error"] = str(e)
                    logger.error(f"Command '{name}' execution failed: {e}")
                    raise
                finally:
                    self._execution_history.append(execution_record)
                    # Keep only last 100 executions
                    if len(self._execution_history) > 100:
                        self._execution_history.pop(0)
            
            # Store command metadata
            command_metadata = {
                "func": wrapper,
                "original_func": func,
                "category": category,
                "description": description or (func.__doc__ or "").split('\n')[0].strip(),
                "deprecated": deprecated,
                "registered_at": datetime.now().isoformat(),
                "execution_count": 0,
            }
            
            self._commands[name] = command_metadata
            
            # Add to category
            if category not in self._categories:
                self._categories[category] = []
            if name not in self._categories[category]:
                self._categories[category].append(name)
            
            # Register aliases
            if aliases:
                for alias in aliases:
                    self._aliases[alias] = name
                    logger.debug(f"Registered alias '{alias}' for command '{name}'")
            
            logger.info(f"Registered command '{name}' in category '{category}'")
            return wrapper
        
        return decorator
    
    def get_command(self, name: str) -> Callable:
        """
        Get a registered command by name or alias.
        
        Args:
            name: The command name or alias
            
        Returns:
            The command function
            
        Raises:
            KeyError: If command is not found
        """
        # Check if it's an alias
        actual_name = self._aliases.get(name, name)
        
        if actual_name not in self._commands:
            available_commands = list(self._commands.keys())
            available_aliases = list(self._aliases.keys())
            raise KeyError(
                f"Command '{name}' not found. "
                f"Available commands: {available_commands}. "
                f"Available aliases: {available_aliases}"
            )
        
        command_info = self._commands[actual_name]
        
        # Warn if deprecated
        if command_info.get("deprecated", False):
            logger.warning(f"Command '{actual_name}' is deprecated")
        
        # Update execution count
        command_info["execution_count"] += 1
        
        return command_info["func"]
    
    def list_commands(self, category: str = None, include_deprecated: bool = True) -> List[str]:
        """
        List all registered command names.
        
        Args:
            category: Filter by category (optional)
            include_deprecated: Include deprecated commands
            
        Returns:
            List of command names
        """
        if category:
            commands = self._categories.get(category, [])
        else:
            commands = list(self._commands.keys())
        
        if not include_deprecated:
            commands = [
                cmd for cmd in commands 
                if not self._commands[cmd].get("deprecated", False)
            ]
        
        return sorted(commands)
    
    def list_categories(self) -> List[str]:
        """List all command categories."""
        return sorted(self._categories.keys())
    
    def get_command_info(self, name: str) -> Dict[str, Any]:
        """
        Get detailed information about a command.
        
        Args:
            name: Command name or alias
            
        Returns:
            Dict containing command information
        """
        actual_name = self._aliases.get(name, name)
        
        if actual_name not in self._commands:
            raise KeyError(f"Command '{name}' not found")
        
        command_info = self._commands[actual_name].copy()
        # Remove the function from the info (not serializable)
        command_info.pop("func", None)
        command_info.pop("original_func", None)
        command_info["name"] = actual_name
        
        # Add alias information
        aliases = [alias for alias, cmd in self._aliases.items() if cmd == actual_name]
        command_info["aliases"] = aliases
        
        return command_info
    
    def has_command(self, name: str) -> bool:
        """
        Check if a command is registered.
        
        Args:
            name: The command name or alias
            
        Returns:
            True if command exists, False otherwise
        """
        actual_name = self._aliases.get(name, name)
        return actual_name in self._commands
    
    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """
        Execute a registered command.
        
        Args:
            name: The command name or alias
            *args: Positional arguments to pass to command
            **kwargs: Keyword arguments to pass to command
            
        Returns:
            Command execution result
        """
        command = self.get_command(name)
        return command(*args, **kwargs)
    
    def add_alias(self, alias: str, command_name: str):
        """
        Add an alias for an existing command.
        
        Args:
            alias: New alias name
            command_name: Existing command name
        """
        if command_name not in self._commands:
            raise KeyError(f"Command '{command_name}' not found")
        
        if alias in self._aliases:
            logger.warning(f"Alias '{alias}' already exists, overriding")
        
        self._aliases[alias] = command_name
        logger.info(f"Added alias '{alias}' for command '{command_name}'")
    
    def remove_command(self, name: str):
        """
        Remove a command from the registry.
        
        Args:
            name: Command name to remove
        """
        if name not in self._commands:
            raise KeyError(f"Command '{name}' not found")
        
        # Remove from commands
        command_info = self._commands.pop(name)
        
        # Remove from category
        category = command_info.get("category", "general")
        if category in self._categories and name in self._categories[category]:
            self._categories[category].remove(name)
            if not self._categories[category]:
                del self._categories[category]
        
        # Remove aliases
        aliases_to_remove = [alias for alias, cmd in self._aliases.items() if cmd == name]
        for alias in aliases_to_remove:
            del self._aliases[alias]
        
        logger.info(f"Removed command '{name}' and {len(aliases_to_remove)} aliases")
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent command execution history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        return self._execution_history[-limit:] if limit > 0 else self._execution_history
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_commands = len(self._commands)
        deprecated_commands = sum(
            1 for cmd in self._commands.values() 
            if cmd.get("deprecated", False)
        )
        
        return {
            "total_commands": total_commands,
            "active_commands": total_commands - deprecated_commands,
            "deprecated_commands": deprecated_commands,
            "total_aliases": len(self._aliases),
            "categories": len(self._categories),
            "execution_history_length": len(self._execution_history),
        }


# Global registry instance
registry = CommandRegistry()

# Convenience function for registration
def register(name: str, **kwargs):
    """Convenience function for command registration."""
    return registry.register(name, **kwargs)

# Backward compatibility aliases
register_command = register
