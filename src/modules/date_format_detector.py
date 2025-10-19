from datetime import datetime
from typing import List, Optional
from src.configuration_and_enums import DateFormats

class DateFormatDetector:
    """Responsible for detecting the date format used in the chat"""

    def __init__(self, date_formats: List[str] = None):
        self.date_formats = date_formats or DateFormats.FORMATS

    def detect_format(self, timestamps: List[str]) -> Optional[str]:
        """
        Detect which date format is used in the provided timestamps

        Args:
            timestamps: List of timestamp strings to analyze

        Returns:
            The matching date format string, or None if no match found
        """
        if not timestamps:
            return None

        return next(
            (
                date_format
                for date_format in self.date_formats
                if self._all_timestamps_match_format(timestamps, date_format)
            ),
            None,
        )

    @staticmethod
    def _all_timestamps_match_format(timestamps: List[str], date_format: str) -> bool:
        """Check if all timestamps match the given format"""
        for timestamp_str in timestamps:
            try:
                datetime.strptime(timestamp_str, date_format)
            except ValueError:
                return False
        return True
