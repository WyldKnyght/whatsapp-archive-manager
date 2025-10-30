# src/modules/media_handler.py

import html
from pathlib import Path
from typing import Optional
from src.configuration_and_enums.special_messages import SpecialMessages
from src.configuration_and_enums.media_type import MediaType
from src.utils.text_utils import TextUtils

class MediaEmbedderInterface:
    """Interface for creating media embeds."""
    def create_embed(self, file_path: Path, media_type: Optional[MediaType], sender_class: str) -> str:
        raise NotImplementedError

class DefaultMediaEmbedder(MediaEmbedderInterface):
    """Default implementation for embedding known media types."""
    def create_embed(self, file_path: Path, media_type: Optional[MediaType], sender_class: str) -> str:
        relative_path = file_path
        # For portability, try/except for relative_path resolution
        try:
            relative_path = file_path.relative_to(file_path.parents[1])
        except Exception:
            relative_path = file_path.name
        if media_type == MediaType.IMAGE:
            return f'<img src="{relative_path}" alt="Image" class="{sender_class}">'
        elif media_type == MediaType.AUDIO:
            return f'<audio controls class="{sender_class}"><source src="{relative_path}"></audio>'
        elif media_type == MediaType.VIDEO:
            return f'<video controls class="{sender_class}"><source src="{relative_path}"></video>'
        elif media_type == MediaType.PDF:
            return f'<a href="{relative_path}" target="_blank" class="{sender_class}">📄 View PDF</a>'
        # Unknown file type
        return f'<span class="{sender_class}">📎 {html.escape(file_path.name)} (unknown type)</span>'

class MediaHandler:
    """Responsible for handling media files and generating media embeds"""

    def __init__(
        self,
        media_folder: Path,
        media_embedder: Optional[MediaEmbedderInterface] = None
    ):
        self.media_folder = media_folder
        self.media_embedder = media_embedder or DefaultMediaEmbedder()

    def create_media_embed(self, message_content: str, sender_class: str) -> str:
        """Create HTML embed for media in message."""
        if message_content.lower() == SpecialMessages.NULL_MESSAGE:
            return self._create_call_indicator(sender_class)
        if SpecialMessages.FILE_ATTACHED in message_content or '<attached:' in message_content:
            return self._create_file_attachment_embed(message_content, sender_class)
        # Regular text
        return f'<span class="{sender_class}">{TextUtils.escape_html(message_content)}</span>'

    @staticmethod
    def _create_call_indicator(sender_class: str) -> str:
        """Create HTML for call indicators."""
        call_type = "Incoming" if sender_class == 'other' else "Outgoing"
        return f'<span class="call-indicator">📞 {call_type} call</span>'

    def _create_file_attachment_embed(self, message_content: str, sender_class: str) -> str:
        """Create HTML embed for file attachments."""
        filename = self._extract_filename(message_content)
        if not filename:
            return f'<span class="{sender_class}">{TextUtils.escape_html(message_content)}</span>'
        media_type = MediaType.from_filename(filename)
        file_path = self.media_folder / filename
        if not file_path.exists():
            return self._create_missing_file_message(filename, sender_class)
        return self.media_embedder.create_embed(file_path, media_type, sender_class)

    @staticmethod
    def _extract_filename(message_content: str) -> Optional[str]:
        if '<attached:' in message_content:
            try:
                return message_content.split('<attached: ')[1].split('>')[0].strip()
            except IndexError:
                return None
        if SpecialMessages.FILE_ATTACHED in message_content:
            parts = message_content.split(SpecialMessages.FILE_ATTACHED)
            if len(parts) > 1:
                return parts[0].strip()
        return None

    @staticmethod
    def _create_missing_file_message(filename: str, sender_class: str) -> str:
        return f'<span class="{sender_class}">📎 {html.escape(filename)} (file not found)</span>'
