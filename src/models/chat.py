"""
Chat data model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

from .message import Message
from .date_range import DateRange

@dataclass
class Chat:
    """Represents a complete chat conversation."""
    
    name: str
    messages: List[Message] = field(default_factory=list)
    sender_color_map: Dict[str, str] = field(default_factory=dict)
    own_name: Optional[str] = None
    date_range: Optional[DateRange] = None
    platform: str = "unknown"  # 'ios' or 'android'
    
    def get_participants(self) -> List[str]:
        """Get list of unique participants."""
        return list({msg.sender for msg in self.messages})
    
    def get_message_count(self) -> int:
        """Get total message count."""
        return len(self.messages)
    
    def get_date_range(self) -> tuple:
        """Get actual date range of messages."""
        if not self.messages:
            return None, None
        
        dates = [msg.timestamp for msg in self.messages]
        return min(dates), max(dates)
    
    def filter_messages(self, date_range: DateRange) -> 'Chat':
        """
        Create a new Chat with filtered messages.
        
        Args:
            date_range: DateRange to filter by
            
        Returns:
            New Chat instance with filtered messages
        """
        filtered_messages = [
            msg for msg in self.messages 
            if date_range.contains(msg.timestamp)
        ]
        
        return Chat(
            name=self.name,
            messages=filtered_messages,
            sender_color_map=self.sender_color_map,
            own_name=self.own_name,
            date_range=date_range,
            platform=self.platform
        )
