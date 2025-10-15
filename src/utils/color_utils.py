"""
Color generation and mapping utilities.
Follows Single Responsibility Principle - only handles color operations.
"""

from typing import Dict, List


class ColorMapper:
    """Handles color mapping for chat participants."""
    
    DEFAULT_COLORS = {
        'own': '#d9fdd3',      # WhatsApp green for own messages
        'default': '#ffffff',   # White for the second sender
        'whatsapp': '#20c063',  # Additional colors for other senders
        'others': [
            '#f0e6ff',  # Light purple
            '#fff3e6',  # Light orange
            '#e6fff0',  # Light mint
            '#ffe6e6',  # Light pink
            '#e6f3ff',  # Light blue
            '#fff0f0',  # Lighter pink
            '#e6ffe6',  # Lighter mint
            '#f2e6ff',  # Lighter purple
            '#fff5e6',  # Peach
            '#e6ffff',  # Light cyan
            '#ffe6f0',  # Rose
            '#f0ffe6',  # Light lime
            '#e6e6ff',  # Lavender
            '#ffe6cc',  # Light apricot
            '#e6fff9'   # Light turquoise
        ]
    }
    
    def __init__(self, own_name: str, colors: Dict = None):
        """
        Initialize color mapper.
        
        Args:
            own_name: Name of the user (gets special color)
            colors: Custom color scheme (optional)
        """
        self.own_name = own_name
        self.colors = colors or self.DEFAULT_COLORS.copy()
        self.sender_color_map: Dict[str, str] = {}
        self._color_index = 0
    
    def get_color_for_sender(self, sender: str) -> str:
        """
        Get color for a sender, assigning a new one if needed.
        
        Args:
            sender: Sender name
            
        Returns:
            Hex color code
        """
        # Return cached color if exists
        if sender in self.sender_color_map:
            return self.sender_color_map[sender]
        
        # Assign color based on sender
        if sender == self.own_name:
            color = self.colors['own']
        elif len(self.sender_color_map) == 0:
            # First other sender gets default color
            color = self.colors['default']
        else:
            # Subsequent senders get colors from the pool
            color = self.colors['others'][self._color_index % len(self.colors['others'])]
            self._color_index += 1
        
        self.sender_color_map[sender] = color
        return color
    
    def generate_color_map(self, senders: List[str]) -> Dict[str, str]:
        """
        Generate color map for all senders at once.
        
        Args:
            senders: List of sender names
            
        Returns:
            Dictionary mapping sender names to colors
        """
        for sender in senders:
            self.get_color_for_sender(sender)
        return self.sender_color_map.copy()
