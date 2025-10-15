"""
Date format detection for WhatsApp messages.
"""

import re
from typing import Optional, List
from datetime import datetime


class DateFormatDetector:
    """Detects date and time formats in WhatsApp chat exports."""
    
    # Common WhatsApp date/time patterns
    PATTERNS = {
        'android': [
            r'\d{1,2}\.\d{1,2}\.\d{2,4},?\s+\d{1,2}:\d{2}',  # DD.MM.YYYY, HH:MM
            r'\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}',    # MM/DD/YYYY, HH:MM
        ],
        'ios': [
            r'\[\d{1,2}\.\d{1,2}\.\d{2,4},?\s+\d{1,2}:\d{2}:\d{2}\]',  # [DD.MM.YYYY, HH:MM:SS]
            r'\[\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}:\d{2}\]',    # [MM/DD/YYYY, HH:MM:SS]
        ]
    }
    
    DATE_FORMATS = {
        'DD.MM.YYYY': '%d.%m.%Y',
        'DD.MM.YY': '%d.%m.%y',
        'MM/DD/YYYY': '%m/%d/%Y',
        'MM/DD/YY': '%m/%d/%y',
    }
    
    @classmethod
    def detect_platform(cls, content: str) -> str:
        """
        Detect if chat is from iOS or Android.
        
        Args:
            content: Chat content
            
        Returns:
            'ios' or 'android'
        """
        # iOS format has timestamps in brackets
        if re.search(r'\[\d{1,2}[./]\d{1,2}[./]\d{2,4}', content[:1000]):
            return 'ios'
        return 'android'
    
    @classmethod
    def detect_date_format(cls, content: str, platform: str) -> str:
        """
        Detect the date format used in the chat.
        
        Args:
            content: Chat content
            platform: 'ios' or 'android'
            
        Returns:
            Date format string (e.g., '%Y.%m.%d')
        """
        patterns = cls.PATTERNS[platform]

        for line in content.split('\n')[:50]:  # Check first 50 lines
            for pattern in patterns:
                if match := re.search(pattern, line):
                    date_str = match.group()
                    return cls._identify_format(date_str)

        # Default to Canadian format
        return '%Y.%m.%d'
    
    @classmethod
    def _identify_format(cls, date_str: str) -> str:
        """Identify specific date format from a matched string."""
        # Remove brackets and time portion
        date_str = date_str.strip('[]').split(',')[0].strip()

        # Try each format
        for format_name, format_str in cls.DATE_FORMATS.items():
            try:
                datetime.strptime(date_str, format_str.replace('%Y', '').replace('%y', ''))
                # Determine if it's 4-digit or 2-digit year
                if len(date_str.split('.')[-1] if '.' in date_str else date_str.split('/')[-1]) == 4:
                    return format_str
                else:
                    return format_str.replace('%Y', '%y')
            except Exception:
                continue

        return '%d.%m.%Y'  # Default

