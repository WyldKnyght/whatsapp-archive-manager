# src/utils/custom_logging/__init__.py
from .setup_logging import setup_logging
from .decorators import error_handler, temporary_log_level
from .setup_file_logging import get_update_logger, enable_file_logging, ConditionalFileHandler

import logging

# Create a pre-configured logger
logger = logging.getLogger(__name__)

__all__ = ['setup_logging', 'error_handler', 'temporary_log_level', 'logger', 'get_update_logger', 'enable_file_logging', 'ConditionalFileHandler']
