"""
A2A Protocol Data Models and Schemas

Implementation of A2A standard data structures for agent discovery,
task management, and inter-agent communication.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field
import uuid


# A2A Protocol Agent Card
@dataclass
class AgentCard:
    """
    A2A Protocol Agent Card for capability discovery.
    
    Follows A2A standard for agent advertisement and discovery.
    """
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    endpoints: Dict[str, str]  # {'tasks': 'http://agent1:8080/tasks', 'status': '...'}
    supported_modalities: List[str]  # ['text', 'json', 'file']
    version: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(cls, agent_id: str, name: str, description: str, 
               capabilities: List[str], endpoints: Dict[str, str],
               supported_modalities: List[str] = None, 
               version: str = "1.0.0", metadata: Dict[str, Any] = None) -> 'AgentCard':
        """Create a new Agent Card with current timestamps."""
        now = datetime.now(timezone.utc)
        return cls(
            agent_id=agent_id,
            name=name,
            description=description,
            capabilities=capabilities,
            endpoints=endpoints,
            supported_modalities=supported_modalities or ['text', 'json'],
            version=version,
            metadata=metadata or {},
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        # Convert datetime to ISO string for JSON serialization
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCard':
        """Create AgentCard from dictionary (Redis retrieval)."""
        # Convert ISO string back to datetime
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


# Task Management Models
class TaskStatus(Enum):
    """A2A Protocol Task Status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    A2A Protocol Task for agent-to-agent communication.
    """
    task_id: str
    task_type: str
    status: TaskStatus
    source_agent_id: str
    target_agent_id: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    @classmethod
    def create(cls, task_type: str, source_agent_id: str, target_agent_id: str,
               parameters: Dict[str, Any], task_id: str = None) -> 'Task':
        """Create a new task with generated ID and timestamps."""
        now = datetime.now(timezone.utc)
        return cls(
            task_id=task_id or str(uuid.uuid4()),
            task_type=task_type,
            status=TaskStatus.CREATED,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            parameters=parameters,
            result=None,
            artifacts=[],
            error_message=None,
            created_at=now,
            updated_at=now,
            started_at=None,
            completed_at=None
        )
    
    def update_status(self, status: TaskStatus, result: Dict[str, Any] = None,
                     error_message: str = None) -> None:
        """Update task status with timestamp tracking."""
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
        
        if status == TaskStatus.RUNNING and not self.started_at:
            self.started_at = self.updated_at
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            self.completed_at = self.updated_at
            
        if result:
            self.result = result
        if error_message:
            self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        # Convert enums and datetime to serializable format
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary (Redis retrieval)."""
        # Convert status back to enum
        data['status'] = TaskStatus(data['status'])
        # Convert datetime strings back to datetime objects
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['started_at'] = datetime.fromisoformat(data['started_at']) if data['started_at'] else None
        data['completed_at'] = datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None
        return cls(**data)


# API Request/Response Models (using Pydantic for validation)
class AgentRegistrationRequest(BaseModel):
    """Request model for agent registration."""
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent description and purpose")
    capabilities: List[str] = Field(..., description="List of agent capabilities")
    endpoints: Dict[str, str] = Field(..., description="Agent service endpoints")
    supported_modalities: List[str] = Field(default=['text', 'json'], description="Supported communication modalities")
    version: str = Field(default="1.0.0", description="Agent version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentDiscoveryRequest(BaseModel):
    """Request model for agent discovery."""
    capabilities: Optional[List[str]] = Field(None, description="Filter by capabilities")
    modalities: Optional[List[str]] = Field(None, description="Filter by supported modalities")
    limit: Optional[int] = Field(10, description="Maximum number of results", ge=1, le=100)


class TaskCreationRequest(BaseModel):
    """Request model for task creation."""
    task_type: str = Field(..., description="Type of task to execute")
    target_agent_id: str = Field(..., description="ID of target agent")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")


class TaskUpdateRequest(BaseModel):
    """Request model for task updates."""
    status: Optional[str] = Field(None, description="New task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# Authentication Models
@dataclass
class APIKey:
    """API Key for agent authentication."""
    key_id: str
    agent_id: str
    key_hash: str  # Hashed API key
    permissions: List[str]  # ['read', 'write', 'admin']
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIKey':
        """Create APIKey from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['expires_at'] = datetime.fromisoformat(data['expires_at']) if data['expires_at'] else None
        return cls(**data)


# Artifact Models for MCP Integration
@dataclass
class Artifact:
    """MCP Protocol Artifact for structured output."""
    artifact_id: str
    artifact_type: str  # 'file', 'data', 'result', 'error'
    content_type: str  # 'application/json', 'text/plain', etc.
    content: Any  # Actual content
    metadata: Dict[str, Any]
    created_by: str  # Agent ID
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artifact':
        """Create Artifact from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


# Configuration Models
class AgentStudioConfig(BaseModel):
    """Configuration for Agent Studio."""
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8080, description="API server port")
    auth_enabled: bool = Field(default=True, description="Enable authentication")
    log_level: str = Field(default="INFO", description="Logging level")
    registry_ttl: int = Field(default=3600, description="Agent registration TTL in seconds")
    task_ttl: int = Field(default=86400, description="Task TTL in seconds")
