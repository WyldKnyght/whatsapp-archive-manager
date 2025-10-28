from typing import List, Set
from src.utils.text_utils import TextUtils


class MessageExtractor:
    """Responsible for extracting messages and metadata from chat lines"""

    @staticmethod
    def extract_timestamps(lines: List[str]) -> List[str]:
        """Extract all timestamps from chat lines"""
        timestamps = []

        for line in lines:
            clean_line = TextUtils.clean_unicode(line)

            # iOS format: [timestamp] ...
            if clean_line.startswith("[") and "]" in clean_line:
                timestamp_str = clean_line.split('] ', 1)[0].replace('[', '')
                timestamps.append(timestamp_str)

            # Android format: timestamp - ...
            elif ' - ' in clean_line and ': ' in clean_line:
                timestamp_str = clean_line.split(' - ', 1)[0]
                timestamps.append(timestamp_str)

        return timestamps

    @staticmethod
    def extract_participant_names(lines: List[str]) -> Set[str]:
        """Extract all participant names from chat lines"""
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
