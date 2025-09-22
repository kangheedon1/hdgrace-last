"""
Logging utilities for HDGRACE.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "hdgrace",
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        format_string: Custom format string (optional)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    logger.setLevel(level_map.get(level.upper(), logging.INFO))
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        
    def log_generation_stats(self, generator_name: str, stats: dict) -> None:
        """Log generation statistics."""
        self.logger.info(
            f"Generator {generator_name} stats: "
            f"generated={stats.get('generated', 0)}, "
            f"cache_hits={stats.get('cache_hits', 0)}, "
            f"cache_hit_rate={stats.get('cache_hits', 0) / max(stats.get('generated', 1), 1):.2%}"
        )
    
    def log_performance_metrics(self, operation: str, duration: float, **kwargs) -> None:
        """Log performance metrics."""
        metrics = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        self.logger.info(f"Performance: {operation} completed in {duration:.3f}s ({metrics})")


class ErrorLogger:
    """Logger for error handling."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_validation_error(self, component: str, error: str, input_data: str = "") -> None:
        """Log validation errors."""
        self.logger.error(f"Validation error in {component}: {error} (input: {input_data[:100]}...)")
    
    def log_generation_error(self, generator: str, error: str, context: dict = None) -> None:
        """Log generation errors."""
        context_str = f" (context: {context})" if context else ""
        self.logger.error(f"Generation error in {generator}: {error}{context_str}")
    
    def log_configuration_error(self, error: str) -> None:
        """Log configuration errors."""
        self.logger.error(f"Configuration error: {error}")