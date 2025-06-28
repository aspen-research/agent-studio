"""
Core ABC Classes

Abstract base classes that define the fundamental interfaces for agents,
executors, main servers, and settings configuration.
Enhanced with A2A protocol compliance and MCP integration.
"""

from .base_agent import BaseAgent
from .base_executor import BaseExecutor  
from .base_main import BaseMain
from .base_settings import BaseSettings, DefaultSettings

__all__ = [
    "BaseAgent",
    "BaseExecutor",
    "BaseMain", 
    "BaseSettings",
    "DefaultSettings",
]
