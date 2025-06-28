"""
Simple Agent Example for Agent Studio

This demonstrates how to create a complete working agent that implements
all required abstract methods from BaseAgent.
"""

import asyncio
import logging
from typing import Dict, Any, AsyncIterable
import uuid
from datetime import datetime

# Import BaseAgent from agent_studio
try:
    import sys
    sys.path.append('/Users/abhiramvaranasi/Desktop/agent-studio')
    from agent_studio import BaseAgent
    AGENT_STUDIO_AVAILABLE = True
except ImportError:
    BaseAgent = object  # Fallback if agent_studio is not available
    AGENT_STUDIO_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleAgent(BaseAgent):
    """A simple agent implementation that properly inherits from BaseAgent."""
    
    def __init__(self, agent_id: str = None):
        if AGENT_STUDIO_AVAILABLE:
            super().__init__(agent_id)
        else:
            self.agent_id = agent_id or "simple_agent"
            self.logger = logging.getLogger(f"{__name__}.{self.agent_id}")
            self._initialized = False
        self._tasks = {}  # Store running tasks
    
    async def initialize(self):
        """Initialize the agent."""
        if not self._initialized:
            self.logger.info(f"Agent {self.agent_id} initializing...")
            await self._setup_resources()
            self._initialized = True
            self.logger.info(f"Agent {self.agent_id} initialized successfully")
    
    async def _setup_resources(self):
        """Setup agent-specific resources."""
        self.logger.info("Setting up agent resources")
        # Add any initialization logic here
    
    async def process_message(
        self, 
        query: str, 
        session_id: str = None, 
        context: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """Process incoming message."""
        session_id = session_id or str(uuid.uuid4())
        
        # Simulate some processing
        self.logger.info(f"Processing message: {query}")
        
        yield {
            "success": True,
            "content": f"Hello! I'm {self.agent_id}. You said: '{query}'",
            "metadata": {
                "agent_id": self.agent_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
            }
        }
        
        # Simulate additional processing steps
        if "weather" in query.lower():
            yield {
                "success": True,
                "content": "I understand you're asking about weather. I'm a simple demo agent, so I can't provide real weather data, but I can help with other tasks!",
                "metadata": {
                    "agent_id": self.agent_id,
                    "session_id": session_id,
                    "step": "weather_response"
                }
            }
        elif "hello" in query.lower() or "hi" in query.lower():
            yield {
                "success": True,
                "content": "Nice to meet you! I'm excited to help. What would you like to do?",
                "metadata": {
                    "agent_id": self.agent_id,
                    "session_id": session_id,
                    "step": "greeting_response"
                }
            }
        else:
            yield {
                "success": True,
                "content": f"I processed your message about '{query}'. This is a demo agent that echoes your input and provides friendly responses.",
                "metadata": {
                    "agent_id": self.agent_id,
                    "session_id": session_id,
                    "step": "general_response"
                }
            }
    
    async def stream(
        self, 
        query: str, 
        session_id: str = None,
        context: Dict[str, Any] = None
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream interface for real-time responses."""
        await self.initialize()
        
        try:
            async for result in self.process_message(query, session_id, context):
                yield result
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            yield {
                "success": False,
                "error": str(e),
                "content": f"❌ Sorry, I encountered an error: {e}",
                "agent_id": self.agent_id,
            }
    
    def get_capabilities(self):
        """Return agent capabilities."""
        return [
            "message_processing",
            "streaming",
            "friendly_conversation",
            "echo_responses"
        ]
    
    def get_status(self):
        """Get agent status."""
        return {
            "agent_id": self.agent_id,
            "initialized": self._initialized,
            "capabilities": self.get_capabilities(),
            "active_tasks": len(self._tasks),
        }
    
    # A2A Protocol Implementation
    def get_agent_card(self) -> Dict[str, Any]:
        """Return Agent Card for A2A capability discovery."""
        return {
            "agent_id": self.agent_id,
            "name": "Simple Demo Agent",
            "description": "A simple demonstration agent for Agent Studio",
            "capabilities": self.get_capabilities(),
            "supported_modalities": ["text", "json"],
            "version": "1.0.0",
            "endpoints": {
                "tasks": f"/agents/{self.agent_id}/tasks",
                "status": f"/agents/{self.agent_id}/status",
                "messages": f"/agents/{self.agent_id}/messages"
            },
            "metadata": {
                "type": "demo_agent",
                "created_at": datetime.now().isoformat()
            }
        }
    
    async def create_task(self, task_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task with lifecycle management."""
        task_id = f"task_{self.agent_id}_{datetime.now().timestamp()}"
        
        task = {
            "task_id": task_id,
            "status": "created",
            "task_type": task_request.get("task_type", "general"),
            "parameters": task_request.get("parameters", {}),
            "created_at": datetime.now().isoformat()
        }
        
        self._tasks[task_id] = task
        self.logger.info(f"Task created: {task_id}")
        
        return task
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current status of a running task."""
        if task_id in self._tasks:
            return self._tasks[task_id]
        else:
            return {"task_id": task_id, "status": "not_found"}
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a running task."""
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "cancelled"
            self._tasks[task_id]["cancelled_at"] = datetime.now().isoformat()
            self.logger.info(f"Task cancelled: {task_id}")
            return {"task_id": task_id, "status": "cancelled"}
        else:
            return {"task_id": task_id, "status": "not_found"}
    
    async def handle_notification(self, notification: Dict[str, Any]) -> None:
        """Handle incoming A2A notifications."""
        notification_type = notification.get("type", "unknown")
        self.logger.info(f"Received notification: {notification_type}")
        # Simple agent just logs notifications
    
    async def negotiate_capabilities(self, client_capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate communication capabilities with client agent."""
        my_modalities = ["text", "json"]
        client_modalities = client_capabilities.get("modalities", [])
        
        # Find common modalities
        common_modalities = list(set(my_modalities) & set(client_modalities))
        
        return {
            "agreed_modalities": common_modalities if common_modalities else ["text"],
            "agent_capabilities": self.get_capabilities(),
            "protocol_version": "1.0"
        }
    
    async def handle_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Process received artifacts from other agents."""
        artifact_id = artifact.get("id", "unknown")
        artifact_type = artifact.get("type", "unknown")
        
        self.logger.info(f"Processing artifact: {artifact_id} (type: {artifact_type})")
        
        # Simple processing - just acknowledge receipt
        return {
            "artifact_id": artifact_id,
            "processed": True,
            "processor_agent": self.agent_id,
            "processed_at": datetime.now().isoformat(),
            "result": f"Artifact {artifact_id} processed by simple agent"
        }
    
    async def process_task(self, task_data: Dict[str, Any]) -> AsyncIterable[Dict[str, Any]]:
        """Process A2A task."""
        task_id = task_data.get("task_id", "unknown")
        task_type = task_data.get("task_type", "general")
        parameters = task_data.get("parameters", {})
        
        self.logger.info(f"Processing A2A task: {task_id} (type: {task_type})")
        
        # Update task status
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "running"
            self._tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        # Process the task based on type
        if task_type == "echo":
            message = parameters.get("message", "Hello from A2A task!")
            yield {
                "success": True,
                "content": f"Echo: {message}",
                "task_id": task_id,
                "task_type": task_type
            }
        elif task_type == "greeting":
            name = parameters.get("name", "friend")
            yield {
                "success": True,
                "content": f"Hello, {name}! Greetings from {self.agent_id}!",
                "task_id": task_id,
                "task_type": task_type
            }
        else:
            # Generic task processing
            yield {
                "success": True,
                "content": f"Processed {task_type} task with parameters: {parameters}",
                "task_id": task_id,
                "task_type": task_type
            }
        
        # Mark task as completed
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["completed_at"] = datetime.now().isoformat()


async def demo_conversation():
    """Demonstrate agent conversation."""
    print("🤖 Simple Agent Demo")
    print("=" * 50)
    
    agent = SimpleAgent("demo_agent")
    
    # Test queries
    test_queries = [
        "Hello there!",
        "What's the weather like?",
        "Can you help me with something?",
        "Tell me about yourself"
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        print("🤖 Agent:")
        
        async for response in agent.stream(query):
            if response["success"]:
                print(f"   {response['content']}")
                if "metadata" in response:
                    meta = response["metadata"]
                    if "step" in meta:
                        print(f"   (Step: {meta['step']})")
            else:
                print(f"   Error: {response.get('error', 'Unknown error')}")
        
        # Small delay between queries for better readability
        await asyncio.sleep(0.5)
    
    print(f"\n📊 Agent Status: {agent.get_status()}")


async def interactive_mode():
    """Interactive chat with the agent."""
    print("🤖 Interactive Agent Chat")
    print("=" * 50)
    print("Type 'quit' or 'exit' to stop")
    
    agent = SimpleAgent("interactive_agent")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 Agent: Goodbye! Thanks for chatting!")
                break
            
            if not user_input:
                continue
            
            print("🤖 Agent:")
            async for response in agent.stream(user_input):
                if response["success"]:
                    print(f"   {response['content']}")
                else:
                    print(f"   Error: {response.get('error', 'Unknown error')}")
        
        except KeyboardInterrupt:
            print("\n🤖 Agent: Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main entry point."""
    print("Agent Studio - Simple Agent Example")
    print("====================================")
    
    mode = input("Choose mode:\n1. Demo conversation\n2. Interactive chat\nEnter 1 or 2: ").strip()
    
    if mode == "2":
        await interactive_mode()
    else:
        await demo_conversation()


if __name__ == "__main__":
    asyncio.run(main())
