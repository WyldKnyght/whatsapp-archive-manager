import html
from typing import List
from src.modules.media_handler import MediaHandler
from src.data_models.chat_metadata import ChatMetadata
from src.data_models import Message
from utils.text_utils import TextUtils

class HTMLGenerator:
    """Responsible for generating HTML output"""

    def __init__(self, css_template: str = None):
        self.css_template = css_template or self._default_css()

    def generate_html(
        self,
        messages: List[Message],
        chat_metadata: ChatMetadata,
        media_handler: MediaHandler
    ) -> str:
        """
        Generate complete HTML document from messages

        Args:
            messages: List of Message objects
            chat_metadata: Metadata about the chat
            media_handler: Handler for media embeds

        Returns:
            Complete HTML document as string
        """
        message_html = self._generate_message_html(messages, chat_metadata, media_handler)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Chat</title>
    <style>
        {self.css_template}
    </style>
</head>
<body>
    <div class="chat-container">
        {message_html}
    </div>
</body>
</html>"""

    def _generate_message_html(
        self,
        messages: List[Message],
        chat_metadata: ChatMetadata,
        media_handler: MediaHandler
    ) -> str:
        """Generate HTML for all messages"""
        html_parts = []

        for message in messages:
            if message.is_system_message:
                html_parts.append(self._create_system_message_html(message))
            else:
                sender_class = 'me' if message.sender == chat_metadata.my_name else 'other'
                html_parts.append(
                    self._create_user_message_html(message, sender_class, media_handler)
                )

        return '\n'.join(html_parts)

    @staticmethod
    def _create_system_message_html(message: Message) -> str:
        """Create HTML for system messages"""
        return f'<div class="system-message">{TextUtils.escape_html(message.content)}</div>'

    @staticmethod
    def _create_user_message_html(
        message: Message,
        sender_class: str,
        media_handler: MediaHandler
    ) -> str:
        """Create HTML for user messages"""
        timestamp_display = message.timestamp.strftime('%Y-%m-%d %H:%M') if message.timestamp else ''
        media_embed = media_handler.create_media_embed(message.content, sender_class)

        return f"""
        <div class="message {sender_class}">
            <div class="sender">{html.escape(message.sender)}</div>
            <div class="timestamp">{timestamp_display}</div>
            <div class="content">{media_embed}</div>
        </div>"""

    @staticmethod
    def _default_css() -> str:
        """Return default CSS styling"""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #e5ddd5;
            margin: 0;
            padding: 20px;
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 70%;
            clear: both;
        }
        .message.me {
            background: #dcf8c6;
            float: right;
            text-align: right;
        }
        .message.other {
            background: white;
            float: left;
            text-align: left;
        }
        .sender {
            font-weight: bold;
            color: #075e54;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        .timestamp {
            font-size: 0.75em;
            color: #667781;
            margin-bottom: 5px;
        }
        .content {
            word-wrap: break-word;
        }
        .content img, .content video {
            max-width: 100%;
            border-radius: 5px;
            margin-top: 5px;
        }
        .content audio {
            width: 100%;
            margin-top: 5px;
        }
        .system-message {
            text-align: center;
            color: #667781;
            font-size: 0.85em;
            margin: 10px 0;
            padding: 5px;
            background: #fff;
            border-radius: 5px;
        }
        .call-indicator {
            font-style: italic;
            color: #667781;
        }
        """
