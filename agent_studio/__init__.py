"""
Agent Studio - A comprehensive framework for building agent-based workflows

A unified framework combining the best of Agent_Final and agentflow systems,
focusing on A2A communication, LangGraph workflows, MCP integration, and 
comprehensive tracing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Agent Studio Team"
__description__ = "A comprehensive framework for building agent-based workflows"

# Import core components for easy access
from .core import (
    BaseAgent,
    BaseExecutor,
    BaseMain,
    BaseSettings,
)

# Import A2A Agent with LangGraph integration (optional)
try:
    from .core.a2a_agent import A2AAgent
except ImportError:
    A2AAgent = None

try:
    from .workflows import (
        BaseLangGraphWorkflow,
        BaseWorkflowState,
    )
except ImportError:
    BaseLangGraphWorkflow = None
    BaseWorkflowState = None

from .management import (
    CommandRegistry,
    register,
)

from .cli import (
    AgentStudioCLI,
)

__all__ = [
    "BaseAgent",
    "BaseExecutor", 
    "BaseMain",
    "BaseSettings",
    "A2AAgent",
    "BaseLangGraphWorkflow",
    "BaseWorkflowState",
    "CommandRegistry",
    "register",
    "AgentStudioCLI",
    "__version__",
    "__author__",
    "__description__",
]
