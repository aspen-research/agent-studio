"""
A2A Agent with LangGraph Workflow Integration

Combines A2A protocol compliance with LangGraph workflow processing,
enabling custom functions that call LLMs, MCP tools, and other services.
"""

import asyncio
import logging
from abc import abstractmethod
from typing import Dict, Any, AsyncIterable, List, Optional
from datetime import datetime, timezone

# LangGraph imports with error handling
try:
    from langgraph.graph import StateGraph, MessagesState
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    StateGraph = None
    MessagesState = None
    ToolNode = None
    LANGGRAPH_AVAILABLE = False

# Agent Studio imports
from .base_agent import BaseAgent


logger = logging.getLogger(__name__)


class A2AAgent(BaseAgent):
    """
    A2A Protocol Agent with LangGraph workflow integration.
    
    This agent handles A2A tasks through LangGraph workflows that can contain:
    - Custom functions calling LLMs
    - MCP tool integrations
    - Business logic processing
    - Multi-step workflows
    """
    
    # A2A Agent Card properties (to be defined by subclasses)
    capabilities: List[str] = []
    supported_modalities: List[str] = ["text", "json"]
    version: str = "1.0.0"
    description: str = "A2A Agent with LangGraph workflow"
    
    def __init__(self, agent_id: str = None, config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        
        # LangGraph workflow
        self.workflow = None
        self.compiled_workflow = None
        
        # LLM and MCP clients (to be initialized)
        self.llm = None
        self.mcp = None
        
        # A2A task tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        
    async def _setup_resources(self):
        """Setup A2A agent resources."""
        self.logger.info(f"🚀 A2A Agent {self.agent_id} initializing...")
        
        # Initialize LLM client
        await self._setup_llm()
        
        # Initialize MCP client
        await self._setup_mcp()
        
        # Build and compile workflow
        self.workflow = self.build_workflow()
        if self.workflow:
            self.compiled_workflow = self.workflow.compile()
            self.logger.info(f"✅ LangGraph workflow compiled for {self.agent_id}")
        
        self.logger.info(f"✅ A2A Agent {self.agent_id} ready with capabilities: {self.capabilities}")
    
    async def _setup_llm(self):
        """Setup LLM client (OpenAI, Anthropic, etc.)"""
        # This will be extended to support multiple LLM providers
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=self.config.get("llm_model", "gpt-4o-mini"),
                temperature=self.config.get("llm_temperature", 0.7)
            )
            self.logger.info("🧠 LLM client initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM client not available: {e}")
            self.llm = None
    
    async def _setup_mcp(self):
        """Setup MCP client for tool execution"""
        try:
            # MCP integration placeholder - implement when MCP client is available
            mcp_config = self.config.get("mcp", {})
            if mcp_config.get("enabled", False):
                self.logger.info("🔧 MCP integration configured but client not implemented yet")
            self.mcp = None  # Will be implemented when MCP client is available
        except Exception as e:
            self.logger.warning(f"⚠️ MCP client not available: {e}")
            self.mcp = None
    
    @abstractmethod
    def build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for this agent.
        
        This method should be implemented by subclasses to define their
        specific workflow with custom functions that call LLMs, MCP tools, etc.
        
        Returns:
            StateGraph: The LangGraph workflow
        """
        pass
    
    async def process_message(
        self, 
        query: str, 
        session_id: str = None, 
        context: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Process message through LangGraph workflow.
        """
        session_id = session_id or f"session_{datetime.now().timestamp()}"
        context = context or {}
        
        self.logger.info(f"📥 A2A Agent {self.agent_id} processing message: '{query[:50]}...'")
        
        if not self.compiled_workflow:
            yield self._create_error_response("No workflow compiled", session_id)
            return
        
        try:
            # Prepare initial state for LangGraph
            initial_state = {
                "messages": [{"role": "user", "content": query}],
                "session_id": session_id,
                "context": context,
                "agent_id": self.agent_id
            }
            
            # Execute workflow and stream results
            async for result in self._execute_workflow_stream(initial_state):
                yield result
                
        except Exception as e:
            self.logger.error(f"❌ Workflow execution error: {e}")
            yield self._create_error_response(str(e), session_id)
    
    async def process_task(self, task_data: Dict[str, Any]) -> AsyncIterable[Dict[str, Any]]:
        """
        Process A2A task through workflow.
        """
        task_id = task_data.get("task_id", f"task_{datetime.now().timestamp()}")
        task_type = task_data.get("task_type", "unknown")
        
        self.logger.info(f"📋 A2A Agent {self.agent_id} processing task: {task_type}")
        
        # Track task
        self.active_tasks[task_id] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc),
            "task_data": task_data
        }
        
        try:
            # Convert A2A task to workflow input
            query = task_data.get("parameters", {}).get("query", "")
            if not query:
                query = f"Process {task_type} task: {task_data.get('parameters', {})}"
            
            # Process through workflow
            async for result in self.process_message(
                query, 
                session_id=task_id, 
                context={"task_data": task_data}
            ):
                # Add A2A task metadata
                result.update({
                    "task_id": task_id,
                    "task_type": task_type,
                    "source_agent": task_data.get("source_agent_id", "unknown")
                })
                yield result
            
            # Mark task completed
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["completed_at"] = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"❌ A2A task processing error: {e}")
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
            yield self._create_error_response(str(e), task_id)
    
    async def _execute_workflow_stream(self, initial_state: Dict[str, Any]) -> AsyncIterable[Dict[str, Any]]:
        """
        Execute LangGraph workflow and stream intermediate results.
        """
        try:
            # Execute workflow
            result = await self.compiled_workflow.ainvoke(initial_state)
            
            # Stream the final result
            yield {
                "success": True,
                "content": self._extract_final_content(result),
                "workflow_result": result,
                "metadata": {
                    "agent_id": self.agent_id,
                    "workflow_completed": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            yield self._create_error_response(f"Workflow error: {str(e)}")
    
    def _extract_final_content(self, workflow_result: Dict[str, Any]) -> str:
        """Extract final content from workflow result."""
        # Try different common patterns for final content
        if "response" in workflow_result:
            return str(workflow_result["response"])
        elif "output" in workflow_result:
            return str(workflow_result["output"])
        elif "messages" in workflow_result and workflow_result["messages"]:
            last_message = workflow_result["messages"][-1]
            if isinstance(last_message, dict):
                return last_message.get("content", str(last_message))
            return str(last_message)
        else:
            return f"Workflow completed: {workflow_result}"
    
    # A2A Protocol Implementation
    def get_agent_card(self) -> Dict[str, Any]:
        """Return A2A Agent Card for discovery."""
        return {
            "agent_id": self.agent_id,
            "name": self.__class__.__name__,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_modalities": self.supported_modalities,
            "version": self.version,
            "endpoints": {
                "tasks": f"/agents/{self.agent_id}/tasks",
                "status": f"/agents/{self.agent_id}/status",
                "messages": f"/agents/{self.agent_id}/messages"
            },
            "metadata": {
                "workflow_enabled": self.compiled_workflow is not None,
                "llm_enabled": self.llm is not None,
                "mcp_enabled": self.mcp is not None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def create_task(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create A2A task."""
        task_id = f"task_{self.agent_id}_{datetime.now().timestamp()}"
        
        task = {
            "task_id": task_id,
            "status": "created",
            "task_type": task_request.get("task_type", "general"),
            "parameters": task_request.get("parameters", {}),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.active_tasks[task_id] = task
        return task
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get A2A task status."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        else:
            return {"task_id": task_id, "status": "not_found"}
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel A2A task."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "cancelled"
            self.active_tasks[task_id]["cancelled_at"] = datetime.now(timezone.utc).isoformat()
            return {"task_id": task_id, "status": "cancelled"}
        else:
            return {"task_id": task_id, "status": "not_found"}
    
    async def handle_notification(self, notification: Dict[str, Any]) -> None:
        """Handle A2A notification."""
        self.logger.info(f"📬 A2A notification received: {notification.get('type', 'unknown')}")
        # Subclasses can override for custom notification handling
    
    async def negotiate_capabilities(self, client_capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate capabilities with client."""
        # Simple capability negotiation
        common_modalities = list(set(self.supported_modalities) & 
                                set(client_capabilities.get("modalities", [])))
        
        return {
            "agreed_modalities": common_modalities,
            "agent_capabilities": self.capabilities,
            "workflow_available": self.compiled_workflow is not None
        }
    
    async def handle_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Handle artifact from another agent."""
        self.logger.info(f"📦 Artifact received: {artifact.get('type', 'unknown')}")
        
        # Basic artifact handling - subclasses can override
        return {
            "artifact_id": artifact.get("id"),
            "processed": True,
            "processor_agent": self.agent_id,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
    
    # Helper methods for workflow functions
    async def llm_call(self, prompt: str, **kwargs) -> str:
        """Helper method for LLM calls in workflow functions."""
        if not self.llm:
            raise RuntimeError("LLM client not available")
        
        response = await self.llm.ainvoke(prompt, **kwargs)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def mcp_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method for MCP tool calls in workflow functions."""
        if not self.mcp:
            raise RuntimeError("MCP client not available")
        
        return await self.mcp.call_tool(tool_name, parameters)
