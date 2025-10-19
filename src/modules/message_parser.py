from datetime import datetime
from typing import List, Optional, Tuple
from src.configuration_and_enums.special_messages import SpecialMessages
from src.data_models import Message
from utils.text_utils import TextUtils


class MessageParser:
    """Responsible for parsing individual messages"""

    def __init__(self, date_format: str, my_name: str):
        self.date_format = date_format
        self.my_name = my_name

    def parse_message(self, message_lines: List[str], last_sender: str) -> Message:
        """
        Parse a message from one or more lines

        Args:
            message_lines: Lines that make up this message
            last_sender: The sender of the previous message (for continuation messages)

        Returns:
            Parsed Message object
        """
        first_line = TextUtils.clean_unicode(message_lines[0])
        rest_of_message = "\n".join(message_lines[1:]).strip()

        if parsed := self._try_parse_structured_message(first_line):
            timestamp_str, content = parsed
            timestamp, sender, message_content = self._parse_message_content(
                timestamp_str, content, first_line, rest_of_message
            )
        else:
            # Continuation of previous message
            timestamp = None
            timestamp_str = ''
            sender = last_sender
            message_content = f"{first_line}\n{rest_of_message}" if rest_of_message else first_line

        return Message(
            timestamp=timestamp,
            sender=sender,
            content=message_content,
            timestamp_str=timestamp_str
        )

    def _try_parse_structured_message(self, line: str) -> Optional[Tuple[str, str]]:
        """Try to parse a line with timestamp and content"""
        # iOS format: [timestamp] content
        if line.startswith("[") and "]" in line:
            parts = line.split('] ', 1)
            if len(parts) == 2:
                return parts[0].replace('[', ''), parts[1]

        # Android format: timestamp - content
        if ' - ' in line and ': ' in line:
            parts = line.split(' - ', 1)
            if len(parts) == 2:
                return parts[0], parts[1]

        return None

    def _parse_message_content(
        self,
        timestamp_str: str,
        content: str,
        first_line: str,
        rest_of_message: str
    ) -> Tuple[Optional[datetime], str, str]:
        """Parse the content portion of a message"""
        try:
            timestamp = datetime.strptime(timestamp_str, self.date_format)

            # Handle "my" messages (prefix with .:)
            if content.startswith(SpecialMessages.MY_MESSAGE_PREFIX):
                sender = self.my_name
                message_content = content[3:]
            else:
                sender, message_content = content.split(': ', 1)

            # Combine with rest of message if present
            if rest_of_message:
                message_content = f"{message_content}\n{rest_of_message}"

            return timestamp, sender.strip(), message_content.strip()

        except ValueError:
            # Failed to parse - treat as continuation
            full_content = f"{first_line}\n{rest_of_message}" if rest_of_message else first_line
            return None, '', full_content
