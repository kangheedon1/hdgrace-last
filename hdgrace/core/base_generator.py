"""
Base generator class providing common functionality.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from collections import defaultdict
from ..utils.config import Config
from ..utils.logger import PerformanceLogger, ErrorLogger

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base class for all generators in HDGRACE.
    
    Provides common functionality including:
    - Caching with LRU eviction
    - Performance monitoring
    - Error handling
    - Statistics tracking
    - Configuration management
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize base generator.
        
        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or Config()
        self.cache = {}
        self.cache_size = self.config.get("cache_size", 1000)
        self.cache_access_times = {}  # For LRU eviction
        self.stats = defaultdict(int)
        self.performance_logger = PerformanceLogger(logger)
        self.error_logger = ErrorLogger(logger)
        
        # Initialize generator-specific data
        self._initialize()
        
        logger.info(f"Initialized {self.__class__.__name__} with cache_size={self.cache_size}")
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize generator-specific data structures."""
        pass
    
    @abstractmethod
    def _generate_content(self, **kwargs) -> Any:
        """
        Core content generation logic - must be implemented by subclasses.
        
        Returns:
            Generated content
        """
        pass
    
    @abstractmethod
    def _validate_input(self, **kwargs) -> None:
        """
        Validate input parameters - must be implemented by subclasses.
        
        Raises:
            ValueError: If input is invalid
        """
        pass
    
    def generate(self, use_cache: bool = True, **kwargs) -> Any:
        """
        Generate content with caching, validation, and performance monitoring.
        
        Args:
            use_cache: Whether to use caching
            **kwargs: Generation parameters
            
        Returns:
            Generated content
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If generation fails
        """
        start_time = time.time()
        
        try:
            # Validate input
            self._validate_input(**kwargs)
            
            # Check cache if enabled
            if use_cache and self.config.get("enable_caching", True):
                cache_key = self._create_cache_key(**kwargs)
                if cache_key in self.cache:
                    self.stats['cache_hits'] += 1
                    self.cache_access_times[cache_key] = time.time()
                    duration = time.time() - start_time
                    self.performance_logger.log_performance_metrics(
                        "generate_cached", duration, cache_hit=True
                    )
                    return self.cache[cache_key]
            
            # Generate new content
            result = self._generate_content(**kwargs)
            self.stats['generated'] += 1
            
            # Cache result if enabled
            if use_cache and self.config.get("enable_caching", True):
                self._cache_result(cache_key, result)
            
            duration = time.time() - start_time
            self.performance_logger.log_performance_metrics(
                "generate_new", duration, cache_hit=False
            )
            
            return result
            
        except ValueError as e:
            self.error_logger.log_validation_error(self.__class__.__name__, str(e), str(kwargs))
            self.stats['validation_errors'] += 1
            raise
        except Exception as e:
            self.error_logger.log_generation_error(self.__class__.__name__, str(e), kwargs)
            self.stats['generation_errors'] += 1
            raise RuntimeError(f"Generation failed: {e}") from e
    
    def _create_cache_key(self, **kwargs) -> str:
        """
        Create a cache key from generation parameters.
        
        Args:
            **kwargs: Generation parameters
            
        Returns:
            Cache key string
        """
        # Sort parameters for consistent key generation
        sorted_items = sorted(kwargs.items())
        return "_".join(f"{k}={v}" for k, v in sorted_items)
    
    def _cache_result(self, cache_key: str, result: Any) -> None:
        """
        Cache generation result with LRU eviction.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        if len(self.cache) >= self.cache_size:
            self._evict_lru_entry()
        
        self.cache[cache_key] = result
        self.cache_access_times[cache_key] = time.time()
    
    def _evict_lru_entry(self) -> None:
        """Evict least recently used cache entry."""
        if not self.cache_access_times:
            return
        
        # Find least recently used entry
        lru_key = min(self.cache_access_times.keys(), 
                     key=lambda k: self.cache_access_times[k])
        
        # Remove from cache
        self.cache.pop(lru_key, None)
        self.cache_access_times.pop(lru_key, None)
        self.stats['cache_evictions'] += 1
    
    def clear_cache(self) -> None:
        """Clear all cached results."""
        self.cache.clear()
        self.cache_access_times.clear()
        self.stats['cache_clears'] += 1
        logger.info(f"{self.__class__.__name__} cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get generation statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = dict(self.stats)
        stats['cache_size'] = len(self.cache)
        
        # Calculate cache hit rate safely
        cache_hits = stats.get('cache_hits', 0)
        generated = stats.get('generated', 0)
        total_requests = cache_hits + generated
        
        stats['cache_hit_rate'] = (
            cache_hits / max(total_requests, 1) if total_requests > 0 else 0.0
        )
        return stats
    
    def log_stats(self) -> None:
        """Log current statistics."""
        self.performance_logger.log_generation_stats(self.__class__.__name__, self.get_stats())
    
    def validate_config(self) -> None:
        """
        Validate generator configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = ['cache_size', 'max_generation_length']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update generator configuration.
        
        Args:
            updates: Configuration updates
        """
        self.config.update(updates)
        self.cache_size = self.config.get("cache_size", 1000)
        
        # Clear cache if cache size changed
        if len(self.cache) > self.cache_size:
            self.clear_cache()
        
        logger.info(f"{self.__class__.__name__} configuration updated")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - log final statistics."""
        self.log_stats()
        return False