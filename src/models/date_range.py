"""
DateRange data model.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DateRange:
    """Represents a date range for filtering messages."""
    
    from_date: Optional[datetime] = None
    until_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate date range after initialization."""
        if self.from_date and self.until_date and self.from_date > self.until_date:
            raise ValueError("From date must be before until date")
    
    def contains(self, msg_date: datetime) -> bool:
        """
        Check if a date falls within this range.
        
        Args:
            msg_date: Date to check
            
        Returns:
            True if date is in range
        """
        if self.from_date and msg_date < self.from_date:
            return False
        return not self.until_date or msg_date <= self.until_date
    
    def is_filtered(self) -> bool:
        """Check if any filtering is applied."""
        return self.from_date is not None or self.until_date is not None
    
    def get_range_string(self) -> str:
        """Get human-readable date range string."""
        if not self.is_filtered():
            return "All messages"
        
        if self.from_date and self.until_date:
            return f"{self.from_date.strftime('%Y-%m-%d')} to {self.until_date.strftime('%Y-%m-%d')}"
        elif self.from_date:
            return f"From {self.from_date.strftime('%Y-%m-%d')}"
        else:
            return f"Until {self.until_date.strftime('%Y-%m-%d')}"
