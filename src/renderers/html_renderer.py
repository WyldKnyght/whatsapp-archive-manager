"""
Main HTML rendering orchestrator.
"""

import os
from pathlib import Path
from typing import List, Set
from datetime import datetime
from src.models.chat import Chat
from .css_generator import CSSGenerator
from .html_builder import HTMLBuilder
from src.io.file_writer import FileWriter


class HTMLRenderer:
    """
    Orchestrates HTML rendering of chat messages.
    Single Responsibility: Coordinate the rendering process.
    """
    
    def __init__(self, output_dir: Path, has_media: bool = False):
        """
        Initialize the HTML renderer.
        
        Args:
            output_dir: Output directory path
            has_media: Whether chat has media attachments
        """
        self.output_dir = Path(output_dir)
        self.has_media = has_media
        self.media_dir = "media" if has_media else None
        self.generated_files: List[Path] = []
        self.css_generator = CSSGenerator()
        self.html_builder = HTMLBuilder()
        self.file_writer = FileWriter()
    
    def render(self, chat: Chat) -> Set[str]:
        """
        Render chat to HTML files.
        
        Args:
            chat: Chat object to render
            
        Returns:
            Set of attachment filenames referenced in rendered messages
        """
        # Generate CSS
        base_css = self.css_generator.generate_base_css()
        color_css = self.css_generator.generate_color_css(chat.sender_color_map)
        full_css = base_css + color_css
        
        # Prepare file paths
        main_file = self.output_dir / "chat.html"
        media_file = self.output_dir / "chat_media_only.html" if self.has_media else None
        
        # Track attachments and dates
        attachments_to_extract: Set[str] = set()
        last_date = None
        
        # Build HTML content
        main_content = ""
        media_content = ""
        
        # Add header
        date_range_str = chat.date_range.get_range_string() if chat.date_range else "All messages"
        header = self.html_builder.build_header(chat.name, date_range_str, len(chat.messages))
        main_content += header
        if self.has_media:
            media_content += header
        
        # Render messages
        for message in chat.messages:
            # Add date separator if date changed
            if last_date is None or message.timestamp.date() != last_date:
                date_sep = self.html_builder.build_date_separator(message.timestamp)
                main_content += date_sep
                if self.has_media:
                    media_content += date_sep
                last_date = message.timestamp.date()
            
            # Get sender CSS class
            sender_class = self._get_sender_class(message.sender)
            is_own = message.sender == chat.own_name
            
            # Build message HTML
            message_html = self.html_builder.build_message(
                message, 
                sender_class, 
                is_own, 
                self.media_dir
            )
            
            # Add to main content
            main_content += message_html
            
            # Add to media content if has attachment
            if self.has_media and message.has_attachment():
                media_content += message_html
                attachments_to_extract.add(message.attachment)
        
        # Add attribution
        attribution = self.html_builder.build_attribution()
        main_content += attribution
        if self.has_media:
            media_content += attribution
        
        # Wrap in HTML document
        main_html = self.html_builder.wrap_in_html(
            f"Chat: {chat.name}",
            full_css,
            main_content
        )
        
        # Write main file
        self.file_writer.write_file(main_file, main_html)
        self.generated_files.append(main_file)
        
        # Write media-only file if needed
        if self.has_media:
            media_html = self.html_builder.wrap_in_html(
                f"Chat Media: {chat.name}",
                full_css,
                media_content
            )
            self.file_writer.write_file(media_file, media_html)
            self.generated_files.append(media_file)
        
        return attachments_to_extract
    
    def _get_sender_class(self, sender: str) -> str:
        """
        Get CSS class for a sender.
        
        Args:
            sender: Sender name
            
        Returns:
            CSS class string
        """
        import re
        safe = re.sub(r'[^a-zA-Z0-9_-]', '-', sender)
        safe = re.sub(r'-+', '-', safe)
        safe = safe.strip('-')
        return f"sender-{safe.lower()}"
    
    def get_generated_files(self) -> List[Path]:
        """Get list of generated file paths."""
        return self.generated_files.copy()
