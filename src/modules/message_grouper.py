from typing import List
from utils.text_utils import TextUtils

class MessageGrouper:
    """Responsible for grouping lines into messages"""

    @staticmethod
    def get_message_start_lines(lines: List[str]) -> List[int]:
        """
        Identify line numbers where new messages start

        Args:
            lines: All lines from the chat file

        Returns:
            List of line indices where messages start
        """
        message_starts = []

        for i, line in enumerate(lines):
            clean_line = TextUtils.clean_unicode(line)

            # iOS format
            if clean_line.startswith("[") and "] " in clean_line:
                message_starts.append(i)

            # Android format
            elif clean_line and ' - ' in clean_line and ': ' in clean_line:
                # Check if line starts with a date pattern
                if clean_line[0].isdigit():
                    message_starts.append(i)

        return message_starts

