"""
Date parsing and validation utilities.
Follows Single Responsibility Principle - only handles date operations.
"""

from datetime import datetime
from typing import Optional


class DateParser:
    """Handles parsing of dates in various formats."""
    
    DEFAULT_FORMATS = [
        "%d.%m.%Y",  # German format: DD.MM.YYYY
        "%m/%d/%Y",  # US format: MM/DD/YYYY
        "%d.%m.%y",  # German format: DD.MM.YY
        "%m/%d/%y"   # US format: MM/DD/YY
    ]
    
    @classmethod
    def parse_date(cls, date_str: str, formats: Optional[list] = None) -> Optional[datetime]:
        """
        Parse a date string using multiple format attempts.
        
        Args:
            date_str: Date string to parse
            formats: List of date format strings to try (optional)
            
        Returns:
            datetime object if successful, None if string is empty
            
        Raises:
            ValueError: If date cannot be parsed in any format
        """
        if not date_str or not date_str.strip():
            return None
            
        date_str = date_str.strip()
        formats_to_try = formats or cls.DEFAULT_FORMATS
        
        for fmt in formats_to_try:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        # If all formats fail, raise an error
        raise ValueError(
            f"Could not parse date '{date_str}'. "
            f"Please use one of these formats: {', '.join(formats_to_try)}"
        )
    
    @classmethod
    def detect_format(cls, date_str: str) -> Optional[str]:
        """
        Detect which format a date string uses.
        
        Args:
            date_str: Date string to analyze
            
        Returns:
            Format string that matches, or None if no match
        """
        for fmt in cls.DEFAULT_FORMATS:
            try:
                datetime.strptime(date_str, fmt)
                return fmt
            except ValueError:
                continue
        return None


class DateValidator:
    """Validates date ranges and relationships."""
    
    @staticmethod
    def validate_range(from_date: Optional[datetime], 
                      until_date: Optional[datetime]) -> bool:
        """
        Validate that from_date is before until_date.
        
        Args:
            from_date: Start date
            until_date: End date
            
        Returns:
            True if valid or either date is None
            
        Raises:
            ValueError: If from_date is after until_date
        """
        if from_date and until_date and from_date > until_date:
            raise ValueError("From date must be before until date")
        return True
    
    @staticmethod
    def is_date_in_range(date: datetime, 
                        from_date: Optional[datetime], 
                        until_date: Optional[datetime]) -> bool:
        """
        Check if a date falls within a range.
        
        Args:
            date: Date to check
            from_date: Start of range (inclusive)
            until_date: End of range (inclusive)
            
        Returns:
            True if date is in range, False otherwise
        """
        if from_date and date < from_date:
            return False
        return not until_date or date <= until_date
