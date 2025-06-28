"""
Base Agent Abstract Class

Enhanced implementation with A2A protocol compliance, MCP integration,
and comprehensive tracing capabilities.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterable, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for A2A protocol agents with LangGraph workflow integration.
    
    Features:
    - A2A protocol compliance (discovery, task lifecycle)
    - LangGraph workflow engine for task processing
    - MCP tool integration
    - LLM integration (OpenAI, Anthropic, etc.)
    - Monitoring, tracing, and error handling
    - Custom function support within workflows
    """

    def __init__(self, agent_id: str = None, config: Dict[str, Any] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            config: Configuration dictionary
        """
        self.agent_id = agent_id or self.__class__.__name__
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.agent_id}")
        self._initialized = False
        
    async def initialize(self):
        """Initialize the agent with necessary resources."""
        if not self._initialized:
            try:
                await self._setup_resources()
                self._initialized = True
                self.logger.info(f"Agent {self.agent_id} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
                raise

    @abstractmethod
    async def _setup_resources(self):
        """Setup agent-specific resources."""
        pass

    @abstractmethod
    async def process_message(
        self, 
        query: str, 
        session_id: str = None, 
        context: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Process incoming message through workflow.
        
        Args:
            query: The input query/message
            session_id: Session identifier for tracking
            context: Additional context information
            
        Yields:
            Dict containing response data
        """
        pass

    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> AsyncIterable[Dict[str, Any]]:
        """
        Process A2A task with comprehensive tracing.
        
        Args:
            task_data: Task configuration and data
            
        Yields:
            Dict containing task execution results
        """
        pass

    async def stream(
        self, 
        query: str, 
        session_id: str = None,
        context: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Stream interface for real-time responses.
        
        Args:
            query: The input query
            session_id: Session identifier
            context: Additional context
            
        Yields:
            Streaming response data
        """
        await self.initialize()
        
        try:
            async for result in self.process_message(query, session_id, context):
                # Add tracing metadata
                result.update({
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": session_id,
                })
                yield result
        except Exception as e:
            self.logger.error(f"Streaming error in {self.agent_id}: {e}")
            yield self._create_error_response(str(e), session_id)

    def _create_error_response(self, error_message: str, session_id: str = None) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "success": False,
            "error": error_message,
            "agent_id": self.agent_id,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": f"❌ Agent Error: {error_message}",
        }

    # Backward compatibility methods
    async def execute(self, *args, **kwargs):
        """Legacy execute method for backward compatibility."""
        self.logger.warning("Using deprecated execute method. Use process_message instead.")
        if args:
            query = str(args[0])
            session_id = kwargs.get('session_id')
            context = kwargs.get('context', {})
            
            results = []
            async for result in self.process_message(query, session_id, context):
                results.append(result)
            return results[-1] if results else None
        return None

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "a2a_protocol",
            "streaming",
            "tracing",
            "mcp_integration",
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "initialized": self._initialized,
            "capabilities": self.get_capabilities(),
            "config_keys": list(self.config.keys()),
        }
    
    # A2A Protocol Methods
    @abstractmethod
    def get_agent_card(self) -> Dict[str, Any]:
        """
        Return Agent Card for A2A capability discovery.
        
        Returns:
            Dict containing agent capabilities, endpoints, and metadata
        """
        pass
    
    @abstractmethod
    async def create_task(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task with lifecycle management.
        
        Args:
            task_request: Task creation request with type, parameters, etc.
            
        Returns:
            Dict containing task_id, status, and metadata
        """
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get current status of a running task.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Dict containing task status, progress, and artifacts
        """
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a running task.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Dict containing cancellation status
        """
        pass
    
    @abstractmethod
    async def handle_notification(self, notification: Dict[str, Any]) -> None:
        """
        Handle incoming A2A notifications.
        
        Args:
            notification: Notification data from other agents
        """
        pass
    
    @abstractmethod
    async def negotiate_capabilities(self, client_capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Negotiate communication capabilities with client agent.
        
        Args:
            client_capabilities: Client's supported modalities and formats
            
        Returns:
            Dict containing agreed-upon communication parameters
        """
        pass
    
    @abstractmethod
    async def handle_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process received artifacts from other agents.
        
        Args:
            artifact: Structured data/output from another agent
            
        Returns:
            Dict containing processing result and any derived artifacts
        """
        pass
