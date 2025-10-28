# src/data_models/__init__.py
"""
Data models for the WhatsApp Archive Manager.

This package contains:
- Message: Represents a single WhatsApp message
- ChatMetadata: Metadata about a chat conversation
"""

from .message import Message
from .chat_metadata import ChatMetadata

__all__ = [
    'Message',
    'ChatMetadata'
]
