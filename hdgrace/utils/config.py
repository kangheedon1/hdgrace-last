"""
Configuration management for HDGRACE.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager with validation and error handling."""
    
    DEFAULT_CONFIG = {
        "cache_size": 1000,
        "max_generation_length": 10000,
        "default_pattern": "lorem",
        "default_format": "paragraph",
        "log_level": "INFO",
        "performance_mode": "balanced",
        "enable_caching": True,
        "enable_statistics": True,
        "max_retries": 3,
        "timeout_seconds": 30
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_path = config_path
        
        if config_path and Path(config_path).exists():
            self.load_from_file(config_path)
        
        self._validate_config()
    
    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            ValueError: If configuration file is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Merge with defaults
            self._config.update(file_config)
            logger.info(f"Configuration loaded from {config_path}")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    def save_to_file(self, config_path: str) -> None:
        """
        Save current configuration to JSON file.
        
        Args:
            config_path: Path where to save configuration
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            raise IOError(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self._validate_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of configuration updates
        """
        self._config.update(updates)
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        cache_size = self._config.get("cache_size", 0)
        if not isinstance(cache_size, int) or cache_size < 0:
            raise ValueError("cache_size must be a non-negative integer")
        
        max_length = self._config.get("max_generation_length", 0)
        if not isinstance(max_length, int) or max_length <= 0:
            raise ValueError("max_generation_length must be a positive integer")
        
        timeout = self._config.get("timeout_seconds", 0)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("timeout_seconds must be a positive number")
        
        retries = self._config.get("max_retries", 0)
        if not isinstance(retries, int) or retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access."""
        return self._config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-like assignment."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator."""
        return key in self._config