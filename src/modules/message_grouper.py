# src/modules/message_grouper.py

from typing import List
from src.utils.text_utils import TextUtils

class MessageStartStrategyInterface:
    """Strategy interface for identifying message start lines."""
    def get_message_start_lines(self, lines: List[str]) -> List[int]:
        raise NotImplementedError

class DefaultMessageStartStrategy(MessageStartStrategyInterface):
    """Default implementation covering iOS and Android formats."""
    def get_message_start_lines(self, lines: List[str]) -> List[int]:
        message_starts = []
        for i, line in enumerate(lines):
            clean_line = TextUtils.clean_unicode(line)
            if clean_line.startswith("[") and "] " in clean_line:
                message_starts.append(i)
            elif clean_line and ' - ' in clean_line and ': ' in clean_line:
                # Android format: starts with a digit (likely date)
                if clean_line[0].isdigit():
                    message_starts.append(i)
        return message_starts

class MessageGrouper:
    """Responsible for grouping lines into messages."""

    def __init__(self, start_strategy: MessageStartStrategyInterface = None):
        self.start_strategy = start_strategy or DefaultMessageStartStrategy()

    def get_message_start_lines(self, lines: List[str]) -> List[int]:
        """
        Identify line numbers where new messages start using the selected strategy.

        Args:
            lines: All lines from the chat file
        Returns:
            List of line indices where messages start
        """
        return self.start_strategy.get_message_start_lines(lines)
