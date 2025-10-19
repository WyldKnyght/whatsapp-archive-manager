import os
import html
import glob
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set, Tuple


# ============================================================================
# UTILITY FUNCTIONS (DRY Principle)
# ============================================================================

class TextUtils:
    """Utility functions for text processing"""

    UNICODE_CHARS_TO_REMOVE = ['\u200e', '\u202f']

    @staticmethod
    def clean_unicode(text: str) -> str:
        """Remove special unicode characters from text"""
        for char in TextUtils.UNICODE_CHARS_TO_REMOVE:
            text = text.replace(char, '')
        return text.strip()

    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters and preserve whitespace"""
        return html.escape(text).replace('\n', '<br>')
