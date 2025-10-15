"""
Sender extraction from WhatsApp messages.
"""

import re
from typing import List, Set

class SenderExtractor:
    """Extracts participant names from chat content."""
    
    @staticmethod
    def extract_senders(content: str, platform: str) -> List[str]:
        """
        Extract all unique sender names from chat content.
        
        Args:
            content: Chat content
            platform: 'ios' or 'android'
            
        Returns:
            Sorted list of unique sender names
        """
        senders: Set[str] = set()

        # Use a universal pattern covering iOS/desktop and Android
        # This matches: [date, time] Name: [message...]
        # or for Android: date - Name: [message...]

        # For your format: [2025-08-23, 9:19:02 PM] Haley: text
        pattern = re.compile(r"\[.*?\]\s*([^\:]+):")

        for line in content.split('\n'):
            if match := pattern.match(line):
                sender = match[1].strip()
                if not SenderExtractor._is_system_message(sender):
                    senders.add(sender)

        return sorted(list(senders))
    
    @staticmethod
    def _is_system_message(sender: str) -> bool:
        """Check if a sender name indicates a system message."""
        system_indicators = [
            'Messages and calls are end-to-end encrypted',
            'Security code changed',
            'changed the group',
            'left',
            'added',
            'removed',
        ]
        return any(indicator in sender for indicator in system_indicators)
