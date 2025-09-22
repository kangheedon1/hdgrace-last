"""
Tests for HDGRACE configuration management.
"""

import pytest
import tempfile
import json
from pathlib import Path
from hdgrace.utils.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_config_initialization(self):
        """Test config initialization with defaults."""
        config = Config()
        
        assert config.get("cache_size") == 1000
        assert config.get("max_generation_length") == 10000
        assert config.get("default_pattern") == "lorem"
        assert config.get("enable_caching") is True
    
    def test_config_from_file(self):
        """Test loading configuration from file."""
        config_data = {
            "cache_size": 2000,
            "custom_setting": "test_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config = Config(config_path)
            
            assert config.get("cache_size") == 2000
            assert config.get("custom_setting") == "test_value"
            assert config.get("default_pattern") == "lorem"  # Default should still be there
        finally:
            Path(config_path).unlink()
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        
        # Test invalid cache size
        with pytest.raises(ValueError, match="cache_size must be a non-negative integer"):
            config.set("cache_size", -1)
        
        # Test invalid max generation length
        with pytest.raises(ValueError, match="max_generation_length must be a positive integer"):
            config.set("max_generation_length", 0)
        
        # Test invalid timeout
        with pytest.raises(ValueError, match="timeout_seconds must be a positive number"):
            config.set("timeout_seconds", -5)
    
    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        config = Config()
        
        # Test get with default
        assert config.get("nonexistent", "default") == "default"
        
        # Test set and get
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
    
    def test_config_update(self):
        """Test updating multiple configuration values."""
        config = Config()
        
        updates = {
            "cache_size": 1500,
            "new_setting": "new_value"
        }
        
        config.update(updates)
        
        assert config.get("cache_size") == 1500
        assert config.get("new_setting") == "new_value"
    
    def test_config_dict_access(self):
        """Test dictionary-like access to configuration."""
        config = Config()
        
        # Test __getitem__
        assert config["cache_size"] == 1000
        
        # Test __setitem__
        config["test_key"] = "test_value"
        assert config["test_key"] == "test_value"
        
        # Test __contains__
        assert "cache_size" in config
        assert "nonexistent" not in config
    
    def test_config_save_load(self):
        """Test saving and loading configuration."""
        config = Config()
        config.set("test_setting", "test_value")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        
        try:
            # Save configuration
            config.save_to_file(config_path)
            
            # Load into new config instance
            new_config = Config(config_path)
            
            assert new_config.get("test_setting") == "test_value"
            assert new_config.get("cache_size") == 1000  # Default should be preserved
        finally:
            Path(config_path).unlink()
    
    def test_invalid_json_file(self):
        """Test handling of invalid JSON configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON in configuration file"):
                Config(config_path)
        finally:
            Path(config_path).unlink()
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Config()
        config.set("test_key", "test_value")
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["test_key"] == "test_value"
        assert config_dict["cache_size"] == 1000
        
        # Ensure it's a copy, not the original
        config_dict["cache_size"] = 9999
        assert config.get("cache_size") == 1000