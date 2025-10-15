"""
String cleaning and formatting utilities.
Follows Single Responsibility Principle - only handles string operations.
"""

import re
import html


class StringCleaner:
    """Handles cleaning and sanitizing of strings."""
    
    @staticmethod
    def clean_sender_name(sender: str) -> str:
        """
        Clean sender name by removing trailing colons and whitespace.
        
        Args:
            sender: Raw sender name
            
        Returns:
            Cleaned sender name
        """
        return sender.rstrip(':').strip()
    
    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape HTML special characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            HTML-escaped text
        """
        return html.escape(text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text (collapse multiple spaces).
        
        Args:
            text: Text to normalize
            
        Returns:
            Text with normalized whitespace
        """
        return ' '.join(text.split())
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length, adding suffix if truncated.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix


class MessageTextProcessor:
    """Processes message text content."""
    
    # Regex patterns for message formatting
    LINK_PATTERN = re.compile(r'(https?://[^\s]+)')
    BOLD_PATTERN = re.compile(r'\*([^\*]+)\*')
    ITALIC_PATTERN = re.compile(r'_([^_]+)_')
    STRIKETHROUGH_PATTERN = re.compile(r'~([^~]+)~')
    
    @classmethod
    def format_message_text(cls, text: str) -> str:
        """
        Format message text with HTML formatting (links, bold, italic, etc.).
        
        Args:
            text: Raw message text
            
        Returns:
            HTML-formatted text
        """
        # Escape HTML first
        text = StringCleaner.escape_html(text)
        
        # Convert WhatsApp formatting to HTML
        text = cls._convert_links(text)
        text = cls._convert_bold(text)
        text = cls._convert_italic(text)
        text = cls._convert_strikethrough(text)
        
        # Convert newlines to <br>
        text = text.replace('\n', '<br>')
        
        return text
    
    @classmethod
    def _convert_links(cls, text: str) -> str:
        """Convert URLs to HTML links."""
        return cls.LINK_PATTERN.sub(r'<a href="\1" target="_blank">\1</a>', text)
    
    @classmethod
    def _convert_bold(cls, text: str) -> str:
        """Convert *bold* to <strong>bold</strong>."""
        return cls.BOLD_PATTERN.sub(r'<strong>\1</strong>', text)
    
    @classmethod
    def _convert_italic(cls, text: str) -> str:
        """Convert _italic_ to <em>italic</em>."""
        return cls.ITALIC_PATTERN.sub(r'<em>\1</em>', text)
    
    @classmethod
    def _convert_strikethrough(cls, text: str) -> str:
        """Convert ~strikethrough~ to <del>strikethrough</del>."""
        return cls.STRIKETHROUGH_PATTERN.sub(r'<del>\1</del>', text)
