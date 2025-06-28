"""
Base Settings Abstract Class

Abstract base class for configuration and settings management
with support for environment variables, file-based config, and validation.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseSettings(ABC):
    """
    Abstract base class for settings and configuration management.
    
    Provides standardized interface for:
    - Configuration loading and validation
    - Environment variable integration
    - File-based configuration
    - Settings persistence
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the base settings.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._config = {}
        self._defaults = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize settings with loading and validation."""
        if not self._initialized:
            try:
                await self._load_defaults()
                await self._load_config()
                await self._validate_config()
                self._initialized = True
                self.logger.info("Settings initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize settings: {e}")
                raise

    @abstractmethod
    async def _load_defaults(self):
        """Load default configuration values."""
        pass

    @abstractmethod
    async def _validate_config(self):
        """Validate the loaded configuration."""
        pass

    async def _load_config(self):
        """Load configuration from various sources."""
        # Load from defaults
        self._config.update(self._defaults)
        
        # Load from file if specified
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                self._config.update(file_config)
                self.logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file {self.config_path}: {e}")
        
        # Override with environment variables
        self._load_from_environment()

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # This is a simplified implementation
        # In practice, you'd define a mapping of env vars to config keys
        env_mappings = self._get_env_mappings()
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Try to convert to appropriate type
                try:
                    if env_value.lower() in ('true', 'false'):
                        self._config[config_key] = env_value.lower() == 'true'
                    elif env_value.isdigit():
                        self._config[config_key] = int(env_value)
                    else:
                        self._config[config_key] = env_value
                except Exception:
                    self._config[config_key] = env_value

    @abstractmethod
    def _get_env_mappings(self) -> Dict[str, str]:
        """Get mapping of environment variables to config keys."""
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    async def save_config(self, path: Optional[str] = None):
        """Save current configuration to file."""
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("No config path specified for saving")
        
        try:
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config to {save_path}: {e}")
            raise

    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values."""
        self._config.update(updates)

    def get_settings_status(self) -> Dict[str, Any]:
        """Get settings status information."""
        return {
            "initialized": self._initialized,
            "config_path": self.config_path,
            "config_keys": list(self._config.keys()),
            "defaults_count": len(self._defaults),
            "total_settings": len(self._config),
        }


class DefaultSettings(BaseSettings):
    """Default implementation of BaseSettings for basic usage."""
    
    async def _load_defaults(self):
        """Load default configuration values."""
        self._defaults = {
            "debug_mode": False,
            "log_level": "INFO",
            "timeout": 30,
            "max_retries": 3,
            "agent_studio_version": "1.0.0",
        }

    async def _validate_config(self):
        """Validate the loaded configuration."""
        # Basic validation
        if self._config.get("timeout", 0) <= 0:
            raise ValueError("Timeout must be positive")
        
        if self._config.get("max_retries", 0) < 0:
            raise ValueError("Max retries cannot be negative")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self._config.get("log_level") not in valid_log_levels:
            self.logger.warning(f"Invalid log level, defaulting to INFO")
            self._config["log_level"] = "INFO"

    def _get_env_mappings(self) -> Dict[str, str]:
        """Get mapping of environment variables to config keys."""
        return {
            "DEBUG_MODE": "debug_mode",
            "LOG_LEVEL": "log_level",
            "TIMEOUT": "timeout",
            "MAX_RETRIES": "max_retries",
        }
