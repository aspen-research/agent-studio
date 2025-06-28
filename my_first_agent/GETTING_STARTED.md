# Getting Started with Your First Agent

## 🎉 Congratulations!
You've successfully created and run your first Agent Studio agent!

## What You've Accomplished

1. **Installed Agent Studio** in development mode
2. **Created a new project** called `my_first_agent`
3. **Built a working agent** that can:
   - Process messages in real-time
   - Handle different types of queries (weather, greetings, etc.)
   - Stream responses asynchronously
   - Maintain session information
   - Log activities

## How to Run Your Agent

### Demo Mode (Automated conversation)
```bash
python simple_agent.py
# Choose option 1
```

### Interactive Mode (Chat with your agent)
```bash
python simple_agent.py
# Choose option 2
# Then type messages and press Enter
# Type 'quit' to exit
```

## Understanding Your Agent

### Key Components

1. **SimpleAgent Class**: The main agent that processes messages
2. **process_message()**: Core logic for handling user input
3. **stream()**: Real-time response streaming
4. **Initialization**: Setup and resource management

### Agent Capabilities

Your agent can:
- ✅ Respond to greetings (`hello`, `hi`)
- ✅ Handle weather questions
- ✅ Process general queries
- ✅ Stream responses in real-time
- ✅ Maintain conversation context
- ✅ Log all activities

## Next Steps - Customize Your Agent

### 1. Add New Response Types
Edit the `process_message()` method to handle new query types:

```python
elif "joke" in query.lower():
    yield {
        "success": True,
        "content": "Why don't programmers like nature? It has too many bugs!",
        "metadata": {"step": "joke_response"}
    }
```

### 2. Add External APIs
Install additional packages and integrate external services:

```python
import requests

# Add to process_message method
elif "time" in query.lower():
    # Get current time from an API
    response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
    time_data = response.json()
    yield {
        "success": True,
        "content": f"Current UTC time: {time_data['datetime']}",
        "metadata": {"step": "time_response"}
    }
```

### 3. Add Memory/Context
Store conversation history:

```python
def __init__(self, agent_id: str = None):
    # ... existing code ...
    self.conversation_history = []

# In process_message method:
self.conversation_history.append({"query": query, "timestamp": datetime.now()})
```

### 4. Add Complex Workflows
For more advanced agents, use the full Agent Studio framework:

```python
from agent_studio import BaseAgent
# Follow the patterns in the main.py file (after implementing all abstract methods)
```

## Agent Studio CLI Commands

While in the project directory:

```bash
# Get help
agent-studio --help

# Check status
agent-studio status

# List available commands
agent-studio commands

# Run using CLI (when properly configured)
agent-studio run --agent my_first_agent
```

## Project Structure

```
my_first_agent/
├── simple_agent.py          # Your working agent (recommended)
├── main.py                  # Template with full BaseAgent (needs completion)
├── config/                  # Configuration files
├── agents/                  # Additional agent implementations
├── workflows/               # Workflow definitions
├── tests/                   # Test cases
└── requirements.txt         # Dependencies
```

## Troubleshooting

### If you get import errors:
```bash
# Make sure you're in the virtual environment
source ../venv/bin/activate

# Install any missing dependencies
pip install -r requirements.txt
```

### If the agent doesn't respond as expected:
- Check the logs (INFO messages) for debugging information
- Modify the `process_message()` method to add your custom logic
- Test with simple queries first

## Advanced Features to Explore

1. **A2A Communication**: Agent-to-Agent messaging
2. **LangGraph Workflows**: Complex multi-step processes
3. **MCP Integration**: Model Context Protocol support
4. **Tracing & Monitoring**: Comprehensive logging and debugging
5. **Command Management**: Custom CLI commands

## Resources

- **Agent Studio Documentation**: Check the main README.md
- **Examples**: Look in the `examples/` directory
- **Core Components**: Explore `agent_studio/core/` for advanced patterns

Happy building! 🚀
