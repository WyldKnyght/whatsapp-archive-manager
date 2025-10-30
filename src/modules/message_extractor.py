# src/modules/message_extractor.py

from typing import List, Set
from src.utils.text_utils import TextUtils

class TimestampExtractorInterface:
    """Interface for extracting timestamps from chat lines."""
    def extract(self, lines: List[str]) -> List[str]:
        raise NotImplementedError

class DefaultTimestampExtractor(TimestampExtractorInterface):
    """Default implementation for extracting timestamps."""
    def extract(self, lines: List[str]) -> List[str]:
        timestamps = []
        for line in lines:
            clean_line = TextUtils.clean_unicode(line)
            if clean_line.startswith("[") and "]" in clean_line:
                timestamp_str = clean_line.split('] ', 1)[0].replace('[', '')
                timestamps.append(timestamp_str)
            elif ' - ' in clean_line and ': ' in clean_line:
                timestamp_str = clean_line.split(' - ', 1)[0]
                timestamps.append(timestamp_str)
        return timestamps

class ParticipantNameExtractorInterface:
    """Interface for extracting participant names."""
    def extract(self, lines: List[str]) -> Set[str]:
        raise NotImplementedError

class DefaultParticipantNameExtractor(ParticipantNameExtractorInterface):
    """Default implementation for extracting participant names from chat lines."""
    def extract(self, lines: List[str]) -> Set[str]:
        names = set()
        for line in lines:
            clean_line = TextUtils.clean_unicode(line)
            if clean_line.startswith("[") and "]" in clean_line:
                try:
                    content = clean_line.split('] ', 1)[1]
                    if ': ' in content:
                        sender = content.split(': ', 1)[0]
                        if not sender.startswith('.'):
                            names.add(sender)
                except IndexError:
                    continue
        return names

class MessageExtractor:
    """Responsible for extracting messages and metadata from chat lines."""

    def __init__(
        self,
        timestamp_extractor: TimestampExtractorInterface = None,
        participant_extractor: ParticipantNameExtractorInterface = None
    ):
        self.timestamp_extractor = timestamp_extractor or DefaultTimestampExtractor()
        self.participant_extractor = participant_extractor or DefaultParticipantNameExtractor()

    def extract_timestamps(self, lines: List[str]) -> List[str]:
        """Extract all timestamps from chat lines using extractor."""
        return self.timestamp_extractor.extract(lines)

    def extract_participant_names(self, lines: List[str]) -> Set[str]:
        """Extract all participant names from chat lines using extractor."""
        return self.participant_extractor.extract(lines)
