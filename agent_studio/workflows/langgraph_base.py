"""
Enhanced LangGraph Workflow Base

Improved implementation of LangGraph workflows with comprehensive tracing,
MCP integration, and better error handling. Combines best practices from
both Agent_Final and agentflow systems.
"""

import os
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, TypedDict, List, AsyncIterable, Optional, Callable
from datetime import datetime, timezone

try:
    from langgraph.graph import StateGraph, START, END
    from typing_extensions import TypedDict
    LANGGRAPH_AVAILABLE = True
except ImportError:
    # Fallback for environments without LangGraph
    StateGraph = None
    START = "START"
    END = "END"
    from typing import TypedDict
    LANGGRAPH_AVAILABLE = False

logger = logging.getLogger(__name__)


class BaseWorkflowState(TypedDict):
    """
    Enhanced standardized base state that all workflows extend.
    
    Includes improved tracing and MCP integration fields.
    """
    # Core fields
    query: str
    session_id: str
    
    # Enhanced workflow metadata
    workflow_metadata: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]  # Enhanced trace with structured data
    errors: List[Dict[str, Any]]  # Enhanced error tracking
    debug_info: Dict[str, Any]
    
    # MCP integration fields
    mcp_context: Dict[str, Any]
    mcp_resources: List[str]
    
    # A2A protocol fields
    a2a_protocol_version: str
    agent_capabilities: List[str]
    
    # Performance tracking
    execution_metrics: Dict[str, Any]


class BaseLangGraphWorkflow(ABC):
    """
    Enhanced abstract base for LangGraph workflows.
    
    Features:
    - Comprehensive tracing and debugging
    - MCP server integration
    - A2A protocol compliance
    - Improved error handling and recovery
    - Performance monitoring
    - Backward compatibility support
    """

    def __init__(self, workflow_id: str = None, config: Dict[str, Any] = None):
        """
        Initialize the workflow.
        
        Args:
            workflow_id: Unique identifier for this workflow
            config: Configuration dictionary
        """
        self.workflow_id = workflow_id or self.__class__.__name__
        self.config = config or {}
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.logger = logging.getLogger(f"{__name__}.{self.workflow_id}")
        
        self.workflow_graph = None
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        self._execution_history = []
        self._performance_metrics = {}

    async def ensure_initialized(self):
        """Ensure workflow is properly initialized with enhanced error handling."""
        if not self._initialized:
            async with self._initialization_lock:
                if not self._initialized:
                    try:
                        self.workflow_graph = await self._build_workflow_safe()
                        await self._setup_mcp_integration()
                        self._initialized = True
                        self.logger.info(f"Workflow {self.workflow_id} initialized successfully")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize workflow {self.workflow_id}: {e}")
                        raise

    async def _build_workflow_safe(self):
        """Safely build workflow with enhanced error handling."""
        try:
            if not LANGGRAPH_AVAILABLE:
                self.logger.warning("LangGraph not available, using fallback workflow")
                return None
            
            workflow = self.build_workflow()
            if workflow:
                # Add standard nodes
                self.add_standard_nodes(workflow)
                compiled_workflow = workflow.compile()
                self.logger.info(f"Workflow {self.workflow_id} compiled successfully")
                return compiled_workflow
            return None
        except Exception as e:
            self.logger.error(f"Failed to build workflow {self.workflow_id}: {e}")
            return None

    async def _setup_mcp_integration(self):
        """Setup MCP server integration if configured."""
        mcp_config = self.config.get("mcp", {})
        if mcp_config.get("enabled", False):
            try:
                # Initialize MCP resources based on configuration
                await self._initialize_mcp_resources(mcp_config)
                self.logger.info(f"MCP integration setup completed for {self.workflow_id}")
            except Exception as e:
                self.logger.warning(f"MCP integration setup failed: {e}")

    async def _initialize_mcp_resources(self, mcp_config: Dict[str, Any]):
        """Initialize MCP-specific resources."""
        # This would be implemented based on specific MCP requirements
        # For now, we'll just store the configuration
        self._mcp_config = mcp_config
        self.logger.debug(f"MCP configuration stored: {list(mcp_config.keys())}")

    @abstractmethod
    def build_workflow(self) -> Optional[StateGraph]:
        """
        Build the LangGraph workflow.
        
        Returns:
            StateGraph instance or None if LangGraph not available
        """
        pass

    @abstractmethod
    async def process_query(
        self, 
        query: str, 
        session_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process query through workflow.
        
        Args:
            query: The input query
            session_id: Session identifier
            context: Additional context
            
        Returns:
            Dict containing processed results
        """
        pass

    async def stream(
        self, 
        query: str, 
        session_id: str,
        context: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Enhanced streaming interface with comprehensive monitoring.
        
        Args:
            query: The input query
            session_id: Session identifier
            context: Additional context
            
        Yields:
            Streaming workflow execution results
        """
        try:
            start_time = datetime.now(timezone.utc)
            trace_id = f"{self.workflow_id}_{session_id}_{start_time.timestamp()}"
            
            # Create initial state
            initial_state = self._create_initial_state(query, session_id, context, trace_id)
            
            # Execute with tracing
            async for result in self.execute_with_enhanced_tracing(initial_state):
                # Add performance metrics
                result.update({
                    "workflow_id": self.workflow_id,
                    "trace_id": trace_id,
                })
                yield result
                
        except Exception as e:
            self.logger.error(f"Workflow streaming error in {self.workflow_id}: {e}")
            yield self._create_error_result(str(e), session_id)

    def _create_initial_state(
        self, 
        query: str, 
        session_id: str, 
        context: Dict[str, Any] = None,
        trace_id: str = None
    ) -> BaseWorkflowState:
        """Create enhanced initial workflow state."""
        return BaseWorkflowState(
            query=query,
            session_id=session_id,
            workflow_metadata={
                "workflow_id": self.workflow_id,
                "trace_id": trace_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "context": context or {},
            },
            execution_trace=[{
                "step": "initialization",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": {"query_length": len(query)},
            }],
            errors=[],
            debug_info={} if not self.debug_mode else {
                "debug_enabled": True,
                "workflow_config": self.config,
            },
            mcp_context=self.config.get("mcp", {}),
            mcp_resources=[],
            a2a_protocol_version="1.0",
            agent_capabilities=["streaming", "tracing", "mcp"],
            execution_metrics={
                "start_time": datetime.now(timezone.utc).isoformat(),
            }
        )

    async def execute_with_enhanced_tracing(
        self, 
        initial_state: BaseWorkflowState
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute workflow with comprehensive tracing and monitoring."""
        trace_id = initial_state["workflow_metadata"].get("trace_id", "unknown")
        
        try:
            await self.ensure_initialized()
            
            if self.workflow_graph:
                async for result in self._execute_langgraph_workflow(initial_state):
                    yield result
            else:
                result = await self._execute_fallback_workflow(initial_state)
                yield result
                
        except Exception as e:
            self.logger.error(f"Enhanced tracing execution failed: {e}")
            yield self._create_error_result(str(e), trace_id)

    async def _execute_langgraph_workflow(
        self, 
        initial_state: BaseWorkflowState
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute using LangGraph with streaming support."""
        try:
            if not self.workflow_graph:
                raise Exception("Workflow graph not initialized")
            
            # For streaming, we'll use astream if available, otherwise ainvoke
            if hasattr(self.workflow_graph, 'astream'):
                async for result in self.workflow_graph.astream(initial_state):
                    formatted_result = self._format_workflow_result(result)
                    yield formatted_result
            else:
                result = await self.workflow_graph.ainvoke(initial_state)
                yield self._format_workflow_result(result)
                
        except Exception as e:
            self.logger.error(f"LangGraph execution failed: {e}")
            yield await self._execute_fallback_workflow(initial_state)

    async def _execute_fallback_workflow(self, initial_state: BaseWorkflowState) -> Dict[str, Any]:
        """Enhanced fallback execution when LangGraph is not available."""
        try:
            query = initial_state.get("query", "")
            session_id = initial_state.get("session_id", "")
            context = initial_state.get("workflow_metadata", {}).get("context", {})
            
            result = await self.process_query(query, session_id, context)
            
            # Enhance result with tracing data
            result.update({
                "execution_mode": "fallback",
                "workflow_id": self.workflow_id,
                "trace_data": initial_state.get("execution_trace", []),
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fallback workflow execution failed: {e}")
            return self._create_error_result(str(e), initial_state.get("session_id", ""))

    def _format_workflow_result(self, result: Any) -> Dict[str, Any]:
        """Enhanced workflow result formatting."""
        if isinstance(result, dict):
            formatted_result = {
                "success": True,
                "content": result.get("content", ""),
                "metadata": result.get("workflow_metadata", {}),
                "execution_trace": result.get("execution_trace", []),
                "performance_metrics": result.get("execution_metrics", {}),
            }
            
            if self.debug_mode:
                formatted_result["debug_info"] = result.get("debug_info", {})
                
            return formatted_result
        else:
            return {
                "success": True,
                "content": str(result),
                "metadata": {"execution_mode": "simple"},
                "execution_trace": [],
                "performance_metrics": {},
            }

    def _create_error_result(self, error_message: str, session_id: str) -> Dict[str, Any]:
        """Create enhanced standardized error result."""
        return {
            "success": False,
            "content": f"❌ Workflow Error: {error_message}",
            "error": error_message,
            "metadata": {
                "workflow_id": self.workflow_id,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_type": "workflow_execution_error",
            },
            "execution_trace": [{
                "step": "error_handling",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error_message,
            }],
            "debug_info": {} if not self.debug_mode else {
                "error_details": error_message,
                "workflow_state": "error",
                "config": self.config,
            }
        }

    def add_standard_nodes(self, workflow: StateGraph):
        """Add enhanced common nodes that all workflows might need."""
        if workflow is None:
            return
            
        try:
            # Enhanced error handler
            workflow.add_node("error_handler", self._enhanced_error_handler_node)
            
            # Performance tracking node
            workflow.add_node("performance_tracker", self._performance_tracker_node)
            
            if self.debug_mode:
                workflow.add_node("debug_logger", self._enhanced_debug_logger_node)
                
            # MCP integration node if enabled
            if self.config.get("mcp", {}).get("enabled", False):
                workflow.add_node("mcp_processor", self._mcp_processor_node)
                
        except Exception as e:
            self.logger.warning(f"Failed to add standard nodes: {e}")

    async def _enhanced_error_handler_node(self, state: BaseWorkflowState) -> BaseWorkflowState:
        """Enhanced error handling node with comprehensive logging."""
        errors = state.get("errors", [])
        if errors:
            self.logger.warning(f"Workflow errors detected in {self.workflow_id}: {len(errors)} errors")
            
            # Add error handling trace
            state["execution_trace"].append({
                "step": "error_handling",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_count": len(errors),
                "errors": errors[-3:] if len(errors) > 3 else errors,  # Keep last 3 errors
            })
            
        return state

    async def _performance_tracker_node(self, state: BaseWorkflowState) -> BaseWorkflowState:
        """Track performance metrics throughout execution."""
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Update execution metrics
        metrics = state.get("execution_metrics", {})
        if "start_time" in metrics:
            start_time = datetime.fromisoformat(metrics["start_time"].replace("Z", "+00:00"))
            current_time_obj = datetime.now(timezone.utc)
            metrics["current_duration"] = (current_time_obj - start_time).total_seconds()
        
        metrics["last_checkpoint"] = current_time
        state["execution_metrics"] = metrics
        
        return state

    async def _enhanced_debug_logger_node(self, state: BaseWorkflowState) -> BaseWorkflowState:
        """Enhanced debug logging node with structured information."""
        if self.debug_mode:
            debug_info = {
                "current_step": "debug_checkpoint",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "state_keys": list(state.keys()),
                "trace_length": len(state.get("execution_trace", [])),
                "error_count": len(state.get("errors", [])),
            }
            
            self.logger.debug(f"Debug checkpoint for {self.workflow_id}: {debug_info}")
            
            # Add to debug info in state
            current_debug = state.get("debug_info", {})
            current_debug.update(debug_info)
            state["debug_info"] = current_debug
            
        return state

    async def _mcp_processor_node(self, state: BaseWorkflowState) -> BaseWorkflowState:
        """Process MCP-related operations."""
        mcp_context = state.get("mcp_context", {})
        if mcp_context:
            # Add MCP processing logic here
            self.logger.debug(f"Processing MCP context: {list(mcp_context.keys())}")
            
            state["execution_trace"].append({
                "step": "mcp_processing",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mcp_operations": list(mcp_context.keys()),
            })
            
        return state

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        return {
            "workflow_id": self.workflow_id,
            "initialized": self._initialized,
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "debug_mode": self.debug_mode,
            "execution_count": len(self._execution_history),
            "config_keys": list(self.config.keys()),
            "mcp_enabled": self.config.get("mcp", {}).get("enabled", False),
        }

    async def cleanup(self):
        """Cleanup workflow resources."""
        try:
            self._execution_history.clear()
            self._performance_metrics.clear()
            self._initialized = False
            self.logger.info(f"Workflow {self.workflow_id} cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
