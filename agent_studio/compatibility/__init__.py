"""
Compatibility Layer

Provides backward compatibility with Agent_Final and agentflow systems,
ensuring smooth migration and interoperability.
"""

from .legacy_adapters import AgentFinalAdapter, AgentFlowAdapter
from .migration_tools import MigrationHelper

__all__ = [
    "AgentFinalAdapter",
    "AgentFlowAdapter", 
    "MigrationHelper",
]
