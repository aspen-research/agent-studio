"""
Project Settings

Configuration settings for the Agent Studio project.
"""

import os

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Agent configuration
AGENT_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
}

# Workflow configuration
WORKFLOW_CONFIG = {
    "debug_mode": DEBUG,
    "mcp": {
        "enabled": False,
    }
}

# Database configuration (if needed)
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "sqlite:///agent_studio.db"),
}
