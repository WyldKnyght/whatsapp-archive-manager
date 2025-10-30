# src/configuration_and_enums/date_formats.py

from typing import List

class DateFormatConfigInterface:
    """Interface for supported date formats configuration."""
    def get_supported_formats(self) -> List[str]:
        raise NotImplementedError

class DefaultDateFormatConfig(DateFormatConfigInterface):
    """Default configuration for date formats."""
    def get_supported_formats(self) -> List[str]:
        return [
            '%d/%m/%Y, %H:%M:%S',      # Common format
            '%m/%d/%Y, %H:%M:%S',      # Common format
            '%Y/%m/%d, %H:%M:%S',      # Common format
            '%d/%m/%Y, %H:%M',         # Common format (no seconds)
            '%m/%d/%Y, %H:%M',         # Common format (no seconds)
            '%Y/%m/%d, %H:%M',         # Common format (no seconds)
            '%d/%m/%y, %H:%M',         # Android format
            '%m/%d/%y, %H:%M',         # Android format
            '%Y-%m-%d, %H:%M:%S',      # ISO-like format
            '%Y-%m-%dT%H:%M:%S',       # ISO 8601
            '%Y-%m-%dT%H:%M:%S.%f',    # ISO 8601 with microseconds
            '%d-%b-%Y, %H:%M:%S',      # Day-Month-Year
            '%d-%b-%y, %H:%M:%S',      # Day-Month-Year (short)
            '%d %b %Y, %H:%M:%S',      # Day Month Year
            '%d %b %y, %H:%M:%S'       # Day Month Year (short)
        ]

class DateFormats:
    """Configuration for supported date formats. Uses strategy for extensibility."""
    def __init__(self, config: DateFormatConfigInterface = None):
        self.config = config or DefaultDateFormatConfig()

    @property
    def formats(self) -> List[str]:
        return self.config.get_supported_formats()
