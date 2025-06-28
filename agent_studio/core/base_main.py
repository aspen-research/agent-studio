"""
Base Main Abstract Class

Abstract base class for main server implementations that coordinate
multiple agents and handle service lifecycle management.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseMain(ABC):
    """
    Abstract base class for main server implementations.
    
    Provides standardized interface for:
    - Service lifecycle management
    - Agent coordination
    - Resource management
    - Health monitoring
    """

    def __init__(self, main_id: str = None, config: Dict[str, Any] = None):
        """
        Initialize the base main server.
        
        Args:
            main_id: Unique identifier for this main server
            config: Configuration dictionary
        """
        self.main_id = main_id or self.__class__.__name__
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.main_id}")
        self._initialized = False
        self._agents = {}
        self._services = {}
        
    async def initialize(self):
        """Initialize the main server with necessary resources."""
        if not self._initialized:
            try:
                await self._setup_main_server()
                self._initialized = True
                self.logger.info(f"Main server {self.main_id} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize main server {self.main_id}: {e}")
                raise

    @abstractmethod
    async def _setup_main_server(self):
        """Setup main server specific resources."""
        pass

    @abstractmethod
    async def start_services(self):
        """Start all registered services."""
        pass

    @abstractmethod
    async def stop_services(self):
        """Stop all running services."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        pass

    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent with the main server."""
        self._agents[agent_id] = agent_instance
        self.logger.info(f"Registered agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get a registered agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self._agents.keys())

    def get_main_status(self) -> Dict[str, Any]:
        """Get current main server status."""
        return {
            "main_id": self.main_id,
            "initialized": self._initialized,
            "registered_agents": len(self._agents),
            "active_services": len(self._services),
            "config_keys": list(self.config.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
