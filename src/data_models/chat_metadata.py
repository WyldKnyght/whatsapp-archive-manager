from dataclasses import dataclass
from typing import Set

@dataclass
class ChatMetadata:
    """Metadata about the chat being converted"""
    participant_names: Set[str]
    date_format: str
    my_name: str
