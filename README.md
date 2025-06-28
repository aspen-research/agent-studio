# Agent Studio

## Overview

Agent Studio is a comprehensive framework for building and managing agent-based workflows with core focus areas like A2A communication, LangGraph workflows, command management, and tracing capabilities. This framework combines the best features from Agent_Final and agentflow systems into a unified, powerful platform.

## Key Features

- **A2A Communication:** Core protocols for agent communication with standardized interfaces
- **LangGraph Workflows:** Advanced workflow management with comprehensive tracing and debugging
- **Command Management:** Dynamic CLI support with extensible command registry system
- **Tracing Capabilities:** In-depth logging, monitoring, and performance tracking
- **Project Initialization:** Complete project scaffolding and management tools
- **MCP Integration:** Built-in support for MCP server integration
- **Backward Compatibility:** Seamless migration from existing Agent_Final and agentflow systems

## Quick Start

### Installation

#### From Git Repository (Recommended)

```bash
# Install the latest version from Git
pip install git+https://github.com/yourusername/agent-studio.git

# Install with LangGraph support
pip install "git+https://github.com/yourusername/agent-studio.git[langgraph]"

# Install development dependencies
pip install "git+https://github.com/yourusername/agent-studio.git[dev]"

# Install all optional dependencies
pip install "git+https://github.com/yourusername/agent-studio.git[all]"
```

#### From Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-studio.git
cd agent-studio

# Install in development mode
pip install -e .

# Or install with extras
pip install -e ".[langgraph,dev]"
```

#### From PyPI (When Published)

```bash
# Install the package
pip install agent-studio

# Install with LangGraph support
pip install agent-studio[langgraph]

# Install development dependencies
pip install agent-studio[dev]
```

### Create Your First Project

```bash
# Initialize a new project
agent-studio init my_agent_project

# Navigate to the project
cd my_agent_project

# Install dependencies
pip install -r requirements.txt

# Run the project
agent-studio run
```

## Architecture

### Core Components

1. **BaseAgent**: Abstract base class for all agents with A2A protocol compliance
2. **BaseExecutor**: Workflow execution management with resource handling
3. **BaseLangGraphWorkflow**: Enhanced LangGraph workflow implementation
4. **CommandRegistry**: Dynamic command registration and management
5. **AgentStudioCLI**: Comprehensive CLI framework

### Project Structure

```
agent-studio/
├── core/                    # Core abstract base classes
│   ├── base_agent.py       # BaseAgent implementation
│   ├── base_executor.py    # BaseExecutor implementation
│   └── base_settings.py    # Configuration management
├── workflows/               # LangGraph workflow framework
│   └── langgraph_base.py   # Enhanced workflow base class
├── management/              # Command management system
│   ├── command_registry.py # Command registry implementation
│   ├── cli_integration.py  # CLI integration utilities
│   └── commands/           # Built-in management commands
├── cli/                    # Main CLI interface
│   └── main.py            # CLI entry point
├── compatibility/          # Backward compatibility layer
│   ├── legacy_adapters.py # Legacy system adapters
│   └── migration_tools.py # Migration utilities
└── templates/              # Project templates
```

## Integration Strategy

### From Agent_Final

✅ **Preserved Features:**
- A2A protocol implementation
- BaseAgent, BaseExecutor, BaseMain abstractions
- LangGraph workflow integration
- Comprehensive tracing and debugging
- MCP server integration

### From Agentflow

✅ **Preserved Features:**
- Dynamic command registry system
- CLI integration with Click framework
- Management command structure
- Project initialization and scaffolding

### Enhanced Features

🚀 **New Capabilities:**
- Unified command line interface
- Enhanced error handling and recovery
- Performance monitoring and metrics
- Improved project management tools
- Comprehensive testing framework
- Package distribution support

## Usage Examples

### Creating a Custom Agent

```python
from agent_studio import BaseAgent

class MyCustomAgent(BaseAgent):
    async def _setup_resources(self):
        """Setup agent-specific resources."""
        self.logger.info("Initializing custom agent")
    
    async def process_message(self, query: str, session_id: str = None, context: dict = None):
        """Process incoming messages."""
        yield {
            "success": True,
            "content": f"Processed: {query}",
            "metadata": {"agent_id": self.agent_id}
        }
    
    async def process_task(self, task_data: dict):
        """Process A2A tasks."""
        yield {
            "success": True,
            "content": f"Task completed: {task_data}",
            "metadata": {"task_type": "custom"}
        }
```

### Creating a Custom Workflow

```python
from agent_studio import BaseLangGraphWorkflow
from langgraph.graph import StateGraph

class MyWorkflow(BaseLangGraphWorkflow):
    def build_workflow(self):
        workflow = StateGraph(BaseWorkflowState)
        
        # Add your workflow nodes
        workflow.add_node("process_input", self.process_input_node)
        workflow.add_node("generate_response", self.generate_response_node)
        
        # Define workflow edges
        workflow.add_edge("process_input", "generate_response")
        
        return workflow
    
    async def process_query(self, query: str, session_id: str, context: dict = None):
        """Process query through the workflow."""
        initial_state = self._create_initial_state(query, session_id, context)
        result = await self.execute_with_enhanced_tracing(initial_state)
        return result
```

### Using Management Commands

```bash
# List all available commands
agent-studio commands

# Get project status
agent-studio manage status

# Clean project files
agent-studio manage clean

# Validate project structure
agent-studio manage validate

# Show command execution history
agent-studio history
```

### Custom Management Commands

```python
from agent_studio.management import register

@register('my_command', category='custom', description='My custom command')
def my_custom_command(args=None, **kwargs):
    """Implementation of my custom command."""
    print("Executing my custom command")
    return {"status": "success"}
```

## Backward Compatibility

### Migration from Agent_Final

- ✅ All existing BaseAgent implementations work without modification
- ✅ LangGraph workflows are fully compatible
- ✅ A2A protocol implementations preserved
- ⚠️ Some internal APIs may require minor updates

### Migration from Agentflow

- ✅ Command registry system fully compatible
- ✅ Management commands work with minimal changes
- ✅ CLI patterns preserved
- ⚠️ Import paths updated to agent_studio namespace

### Compatibility Layer

```python
# Legacy Agent_Final imports (still supported)
from agent_studio.compatibility import AgentFinalAdapter

# Legacy agentflow imports (still supported)
from agent_studio.compatibility import AgentFlowAdapter
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/agent-studio/agent-studio.git
cd agent-studio

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black agent_studio/

# Type checking
mypy agent_studio/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Testing Strategy

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test component interactions
- **Workflow Tests**: Test complete workflow execution
- **CLI Tests**: Test command-line interface functionality
- **Compatibility Tests**: Ensure backward compatibility

## CLI Reference

### Main Commands

- `agent-studio init <name>` - Initialize new project
- `agent-studio run` - Run agents/workflows
- `agent-studio status` - Show system status
- `agent-studio commands` - List available commands
- `agent-studio manage <command>` - Execute management commands
- `agent-studio history` - Show execution history

### Management Commands

- `init` - Initialize project
- `status` - Project status
- `validate` - Validate project
- `clean` - Clean temporary files

## Configuration

### Project Configuration

```json
{
  "project_name": "my_project",
  "version": "1.0.0",
  "agent_studio_version": "1.0.0",
  "debug_mode": false,
  "mcp": {
    "enabled": false
  }
}
```

### Environment Variables

- `DEBUG_MODE`: Enable debug logging
- `LOG_LEVEL`: Set logging level
- `AGENTSTUDIO_CONFIG`: Custom config file path

## Roadmap

### Version 1.1
- [ ] Enhanced MCP integration
- [ ] Advanced workflow debugging tools
- [ ] Performance optimization
- [ ] Extended template library

### Version 1.2
- [ ] Web UI for project management
- [ ] Distributed workflow execution
- [ ] Plugin system
- [ ] Advanced monitoring dashboard

## Support

- **Documentation**: [https://agent-studio.readthedocs.io/](https://agent-studio.readthedocs.io/)
- **Issues**: [https://github.com/agent-studio/agent-studio/issues](https://github.com/agent-studio/agent-studio/issues)
- **Discussions**: [https://github.com/agent-studio/agent-studio/discussions](https://github.com/agent-studio/agent-studio/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built upon the excellent foundations of Agent_Final and agentflow
- Inspired by Django's management command system
- Powered by LangGraph for workflow management

