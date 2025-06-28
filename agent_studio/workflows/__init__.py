"""
Workflow Framework

Enhanced LangGraph-based workflow framework with built-in tracing, debugging,
and standardized state management. Combines the best features from both systems.
"""

# Import workflows with handling for LangGraph availability
try:
    from .langgraph_base import BaseLangGraphWorkflow, BaseWorkflowState
    WORKFLOWS_AVAILABLE = True
except ImportError:
    BaseLangGraphWorkflow = None
    BaseWorkflowState = None
    WORKFLOWS_AVAILABLE = False

__all__ = [
    "BaseLangGraphWorkflow",
    "BaseWorkflowState",
]
