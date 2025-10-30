# src/configuration_and_enums/media_type.py

from enum import Enum
from typing import List, Optional

class MediaType(Enum):
    """Enumeration of supported media types."""
    IMAGE = ('image', ['.png', '.jpg', '.jpeg', '.gif', '.bmp'])
    AUDIO = ('audio', ['.mp3', '.wav', '.ogg', '.opus'])
    VIDEO = ('video', ['.mp4', '.avi', '.mov', '.wmv'])
    PDF = ('pdf', ['.pdf'])

    def __init__(self, category: str, extensions: List[str]):
        self.category = category
        self.extensions = extensions

    @classmethod
    def from_filename(cls, filename: str) -> Optional['MediaType']:
        """Determine media type from filename extension."""
        lower_filename = filename.lower()
        return next(
            (
                media_type
                for media_type in cls
                if any(lower_filename.endswith(ext) for ext in media_type.extensions)
            ),
            None,
        )
