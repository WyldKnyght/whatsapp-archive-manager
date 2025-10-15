"""
Message data model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Represents a single chat message."""
    
    timestamp: datetime
    sender: str
    text: str
    attachment: Optional[str] = None
    attachment_type: Optional[str] = None
    is_system_message: bool = False
    raw_line: str = field(default="", repr=False)
    
    def has_attachment(self) -> bool:
        """Check if message has an attachment."""
        return self.attachment is not None
    
    def is_media_message(self) -> bool:
        """Check if message is a media message."""
        return self.attachment_type in ['image', 'video', 'audio']
    
    def get_display_time(self) -> str:
        """Get formatted display time."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

