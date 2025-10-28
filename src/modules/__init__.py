# src/modules/__init__.py
"""
Core business logic modules for the WhatsApp Archive Manager.

This package contains all the main processing classes:
- DateFormatDetector: Detects date formats in chat exports
- FileManager: Manages file system operations
- HTMLGenerator: Generates HTML output from messages
- MediaHandler: Handles media file detection and embedding
- MessageExtractor: Extracts raw data from chat lines
- MessageGrouper: Groups chat lines into messages
- MessageParser: Parses individual messages
"""

from .date_format_detector import DateFormatDetector
from .file_manager import FileManager
from .html_generator import HTMLGenerator
from .media_handler import MediaHandler
from .message_extractor import MessageExtractor
from .message_grouper import MessageGrouper
from .message_parser import MessageParser

__all__ = [
    'DateFormatDetector',
    'FileManager',
    'HTMLGenerator',
    'MediaHandler',
    'MessageExtractor',
    'MessageGrouper',
    'MessageParser'
]