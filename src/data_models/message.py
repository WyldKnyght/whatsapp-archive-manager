# src/data_models/message.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    """Represents a single WhatsApp message."""
    timestamp: Optional[datetime]
    sender: str
    content: str
    timestamp_str: str = ''
    is_system_message: bool = False
