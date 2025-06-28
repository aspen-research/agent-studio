"""
Base Executor Abstract Class

Enhanced executor for managing workflow execution, resource handling,
and MCP server integration with comprehensive tracing.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseExecutor(ABC):
    """
    Abstract base class for workflow executors.
    
    Provides standardized interface for:
    - Workflow execution management
    - Resource allocation and cleanup
    - MCP server integration
    - Comprehensive tracing and monitoring
    """

    def __init__(self, executor_id: str = None, config: Dict[str, Any] = None):
        """
        Initialize the base executor.
        
        Args:
            executor_id: Unique identifier for this executor
            config: Configuration dictionary
        """
        self.executor_id = executor_id or self.__class__.__name__
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.executor_id}")
        self._initialized = False
        self._running_tasks = {}
        self._resource_pool = {}
        
    async def initialize(self):
        """Initialize the executor with necessary resources."""
        if not self._initialized:
            try:
                await self._setup_executor()
                self._initialized = True
                self.logger.info(f"Executor {self.executor_id} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize executor {self.executor_id}: {e}")
                raise

    @abstractmethod
    async def _setup_executor(self):
        """Setup executor-specific resources."""
        pass

    @abstractmethod
    async def execute_workflow(
        self,
        workflow_config: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow with given configuration.
        
        Args:
            workflow_config: Workflow configuration and parameters
            context: Execution context
            
        Returns:
            Dict containing execution results
        """
        pass

    @abstractmethod
    async def execute_task(
        self,
        task_config: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a single task.
        
        Args:
            task_config: Task configuration
            context: Execution context
            
        Returns:
            Dict containing task results
        """
        pass

    async def execute_with_tracing(
        self,
        execution_config: Dict[str, Any],
        trace_id: str = None
    ) -> Dict[str, Any]:
        """
        Execute with comprehensive tracing and monitoring.
        
        Args:
            execution_config: Configuration for execution
            trace_id: Unique trace identifier
            
        Returns:
            Dict containing execution results with tracing data
        """
        await self.initialize()
        
        trace_id = trace_id or f"{self.executor_id}_{datetime.now().timestamp()}"
        start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting execution {trace_id}")
        
        try:
            # Determine execution type
            if 'workflow_config' in execution_config:
                result = await self.execute_workflow(
                    execution_config['workflow_config'],
                    execution_config.get('context', {})
                )
            elif 'task_config' in execution_config:
                result = await self.execute_task(
                    execution_config['task_config'],
                    execution_config.get('context', {})
                )
            else:
                raise ValueError("Invalid execution configuration")
            
            # Add tracing metadata
            end_time = datetime.now(timezone.utc)
            result.update({
                "trace_id": trace_id,
                "executor_id": self.executor_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": (end_time - start_time).total_seconds(),
                "success": True,
            })
            
            self.logger.info(f"Execution {trace_id} completed successfully")
            return result
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            error_result = {
                "trace_id": trace_id,
                "executor_id": self.executor_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": (end_time - start_time).total_seconds(),
                "success": False,
                "error": str(e),
                "content": f"❌ Execution Error: {str(e)}",
            }
            
            self.logger.error(f"Execution {trace_id} failed: {e}")
            return error_result

    async def manage_resource(
        self,
        resource_type: str,
        action: str,
        resource_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Manage executor resources (allocate, deallocate, monitor).
        
        Args:
            resource_type: Type of resource to manage
            action: Action to perform (allocate, deallocate, status)
            resource_config: Resource configuration
            
        Returns:
            Dict containing resource management results
        """
        await self.initialize()
        
        try:
            if action == "allocate":
                return await self._allocate_resource(resource_type, resource_config or {})
            elif action == "deallocate":
                return await self._deallocate_resource(resource_type, resource_config or {})
            elif action == "status":
                return self._get_resource_status(resource_type)
            else:
                raise ValueError(f"Invalid resource action: {action}")
                
        except Exception as e:
            self.logger.error(f"Resource management error: {e}")
            return {
                "success": False,
                "error": str(e),
                "resource_type": resource_type,
                "action": action,
            }

    async def _allocate_resource(
        self,
        resource_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Allocate a specific resource."""
        resource_id = f"{resource_type}_{len(self._resource_pool)}"
        self._resource_pool[resource_id] = {
            "type": resource_type,
            "config": config,
            "allocated_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }
        
        self.logger.info(f"Resource {resource_id} allocated")
        return {
            "success": True,
            "resource_id": resource_id,
            "resource_type": resource_type,
        }

    async def _deallocate_resource(
        self,
        resource_type: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deallocate a specific resource."""
        resource_id = config.get("resource_id")
        if resource_id and resource_id in self._resource_pool:
            del self._resource_pool[resource_id]
            self.logger.info(f"Resource {resource_id} deallocated")
            return {
                "success": True,
                "resource_id": resource_id,
            }
        else:
            return {
                "success": False,
                "error": f"Resource {resource_id} not found",
            }

    def _get_resource_status(self, resource_type: str = None) -> Dict[str, Any]:
        """Get status of resources."""
        if resource_type:
            resources = {
                k: v for k, v in self._resource_pool.items() 
                if v["type"] == resource_type
            }
        else:
            resources = self._resource_pool.copy()
            
        return {
            "success": True,
            "resources": resources,
            "total_count": len(resources),
        }

    def get_executor_status(self) -> Dict[str, Any]:
        """Get current executor status."""
        return {
            "executor_id": self.executor_id,
            "initialized": self._initialized,
            "running_tasks": len(self._running_tasks),
            "allocated_resources": len(self._resource_pool),
            "config_keys": list(self.config.keys()),
        }

    async def cleanup(self):
        """Cleanup executor resources."""
        try:
            # Cancel running tasks
            for task_id, task in self._running_tasks.items():
                if not task.done():
                    task.cancel()
                    self.logger.info(f"Cancelled task {task_id}")
            
            # Cleanup resources
            self._resource_pool.clear()
            self._running_tasks.clear()
            
            self.logger.info(f"Executor {self.executor_id} cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        if self._initialized:
            try:
                asyncio.create_task(self.cleanup())
            except Exception:
                pass  # Best effort cleanup
