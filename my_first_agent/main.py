"""
my_first_agent - Agent Studio Project

Main entry point for the my_first_agent agent system.
"""

import asyncio
import logging
from agent_studio import BaseAgent, BaseLangGraphWorkflow

logger = logging.getLogger(__name__)


class My_first_agentAgent(BaseAgent):
    """Main agent for my_first_agent."""
    
    async def _setup_resources(self):
        """Setup agent resources."""
        logger.info("Setting up my_first_agent agent resources")
    
    async def process_message(self, query: str, session_id: str = None, context: dict = None):
        """Process incoming messages."""
        yield {
            "success": True,
            "content": f"Hello from my_first_agent! Your query: {query}",
            "metadata": {"agent": "my_first_agent"},
        }
    
    async def process_task(self, task_data: dict):
        """Process A2A tasks."""
        yield {
            "success": True,
            "content": f"Task processed: {task_data}",
            "metadata": {"agent": "my_first_agent"},
        }


async def main():
    """Main entry point."""
    agent = My_first_agentAgent(agent_id="my_first_agent")
    
    # Example usage
    async for result in agent.stream("Hello, Agent Studio!"):
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
