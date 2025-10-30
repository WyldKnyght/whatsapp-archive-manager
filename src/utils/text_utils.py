# src/utils/text_utils.py

import html

class TextUtils:
    """Utility functions for text processing."""

    UNICODE_CHARS_TO_REMOVE = ['\u200e', '\u202f']

    @staticmethod
    def clean_unicode(text: str) -> str:
        """Remove special unicode characters from text and strip whitespace."""
        for char in TextUtils.UNICODE_CHARS_TO_REMOVE:
            text = text.replace(char, '')
        return text.strip()

    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters and preserve line breaks as <br>."""
        return html.escape(text).replace('\n', '<br>')
