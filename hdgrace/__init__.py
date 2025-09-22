"""
HDGRACE - High-Definition Generator and Runtime Application Code Engine
Production-ready refactored version with improved maintainability and performance.
"""

__version__ = "2.0.0"
__author__ = "HDGRACE Development Team"

from .core.base_generator import BaseGenerator
from .generators.text_generator import TextGenerator
from .generators.code_generator import CodeGenerator
from .generators.data_generator import DataGenerator
from .utils.logger import setup_logger
from .utils.config import Config

__all__ = [
    'BaseGenerator',
    'TextGenerator',
    'CodeGenerator', 
    'DataGenerator',
    'setup_logger',
    'Config'
]