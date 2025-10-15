"""
HTML structure building for chat export.
"""

from datetime import datetime
from typing import Optional
from src.models.message import Message
from src.utils.string_utils import MessageTextProcessor


class HTMLBuilder:
    """
    Builds HTML structures for chat messages.
    Single Responsibility: Only HTML structure building.
    """
    
    @staticmethod
    def build_header(chat_name: str, date_range_str: str, 
                    message_count: int) -> str:
        """
        Build HTML header section.
        
        Args:
            chat_name: Name of the chat
            date_range_str: Human-readable date range
            message_count: Total message count
            
        Returns:
            HTML string
        """
        return f"""
        <div class="chat-header">
            <h1 class="chat-title">{chat_name}</h1>
            <p class="chat-info">
                {date_range_str} • {message_count} messages
            </p>
        </div>
        """
    
    @staticmethod
    def build_date_separator(date: datetime) -> str:
        """
        Build date separator HTML.
        
        Args:
            date: Date to display
            
        Returns:
            HTML string
        """
        date_str = date.strftime("%B %d, %Y")
        return f"""
        <div class="date-separator">
            <span>{date_str}</span>
        </div>
        <div class="clearfix"></div>
        """
    
    @staticmethod
    def build_message(message: Message, sender_class: str, 
                     is_own: bool, media_dir: Optional[str] = None) -> str:
        """
        Build HTML for a single message.
        
        Args:
            message: Message object
            sender_class: CSS class for sender
            is_own: Whether this is user's own message
            media_dir: Path to media directory (optional)
            
        Returns:
            HTML string
        """
        if message.is_system_message:
            return HTMLBuilder._build_system_message(message)
        
        # Build message div with classes
        classes = ["message", sender_class]
        if is_own:
            classes.append("own")
        else:
            classes.append("other")
        
        class_str = " ".join(classes)
        
        # Format message text
        formatted_text = MessageTextProcessor.format_message_text(message.text)
        
        # Build attachment HTML if present
        attachment_html = ""
        if message.has_attachment() and media_dir:
            attachment_html = HTMLBuilder._build_attachment(
                message.attachment, 
                message.attachment_type, 
                media_dir
            )
        
        # Build complete message HTML
        html = f'<div class="{class_str}">\n'
        if not is_own:
            html += f'  <div class="message-sender">{message.sender}</div>\n'
        html += f'  <div class="message-text">{formatted_text}</div>\n'
        if attachment_html:
            html += f'  <div class="message-attachment">{attachment_html}</div>\n'
        html += f'  <div class="message-time">{message.get_display_time()}</div>\n'
        html += '</div>\n'
        html += '<div class="clearfix"></div>\n'
        
        return html
    
    @staticmethod
    def _build_system_message(message: Message) -> str:
        """Build HTML for system message."""
        return f"""
        <div class="system-message">
            {message.text}
        </div>
        """
    
    @staticmethod
    def _build_attachment(filename: str, att_type: str, media_dir: str) -> str:
        """
        Build HTML for message attachment.
        
        Args:
            filename: Attachment filename
            att_type: Attachment type (image, video, etc.)
            media_dir: Media directory path
            
        Returns:
            HTML string
        """
        file_path = f"{media_dir}/{filename}"
        
        if att_type == 'image':
            return f'<img src="{file_path}" alt="{filename}" loading="lazy">'
        elif att_type == 'video':
            return f'<video src="{file_path}" controls></video>'
        elif att_type == 'audio':
            return f'<audio src="{file_path}" controls></audio>'
        else:
            return f'<a href="{file_path}" download>{filename}</a>'
    
    @staticmethod
    def build_attribution() -> str:
        """Build attribution footer."""
        return """
        <div class="attribution">
            This chat was created with WhatsApp Archive Manager. 
        </div>
        """
    
    @staticmethod
    def wrap_in_html(title: str, css: str, body_content: str) -> str:
        """
        Wrap content in complete HTML document.
        
        Args:
            title: Page title
            css: CSS styles
            body_content: Body HTML content
            
        Returns:
            Complete HTML document
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css}
    </style>
</head>
<body>
    <div class="chat-container">
        {body_content}
    </div>
</body>
</html>
"""
