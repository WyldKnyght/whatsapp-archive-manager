import re
from datetime import datetime
from typing import List, Optional, Tuple
from src.configuration_and_enums.special_messages import SpecialMessages
from src.data_models import Message
from src.utils.text_utils import TextUtils
from src.configuration_and_enums.format_detector import FormatDetector, WhatsAppFormat

def normalize_compact_time(time_str: str) -> str:
    """
    Converts '91312 PM' -> '09:13:12 PM'
    """
    if m := re.match(r'^(\d{1,2})(\d{2})(\d{2}) ?([AP]M)$', time_str.strip()):
        hh, mm, ss, ampm = m.groups()
        hh = hh.zfill(2)
        return f"{hh}:{mm}:{ss} {ampm}"
    return time_str

class WhatsAppMessageParser:
    def __init__(self, file_path: str, my_name: str = None):
        self.file_path = file_path
        self.encoding, _ = FormatDetector.detect_encoding(file_path)
        self.format_type, self.confidence, _ = FormatDetector.detect_format(file_path, self.encoding)
        if self.format_type == WhatsAppFormat.UNKNOWN:
            raise ValueError(f"Unknown or unsupported WhatsApp format in {file_path}")
        self.format_info = FormatDetector.get_format_info(self.format_type)
        self.pattern = re.compile(self.format_info.regex)
        self.date_format = f"{self.format_info.date_format} {self.format_info.time_format}"
        self.my_name = my_name

    def parse(self) -> List[Message]:
        messages = []
        current_lines = []
        last_sender = None
        def clean_line(l):
            return l.replace('\u202f', ' ').replace('\xa0', ' ')
        with open(self.file_path, 'r', encoding=self.encoding, errors='replace') as f:
            lines = [clean_line(line.strip()) for line in f]
            for line in lines:
                match = self.pattern.match(line)
                if match:
                    if current_lines:
                        messages.append(self._parse_message(current_lines, last_sender))
                    groups = match.groups()
                    if self.format_type == WhatsAppFormat.US_BRACKET_AMPMPM:
                        date_str, time_str, am_pm, sender, content = groups
                        full_time_str = f"{time_str}{am_pm}"
                        current_lines = [f"{date_str} {full_time_str} - {sender}: {content}"]
                        last_sender = sender
                    elif self.format_type == WhatsAppFormat.US_COMMA_COMPACT:
                        date_str, time_str, sender, content = groups
                        full_time_str = normalize_compact_time(time_str)
                        current_lines = [f"{date_str} {full_time_str} - {sender}: {content}"]
                        last_sender = sender
                    elif len(groups) == 4:
                        date_str, time_str, sender, content = groups
                        current_lines = [f"{date_str} {time_str} - {sender}: {content}"]
                        last_sender = sender
                    else:
                        current_lines = [line]
                elif current_lines:
                    current_lines.append(line)
            if current_lines:
                messages.append(self._parse_message(current_lines, last_sender))
        return messages

    def _parse_message(self, message_lines: List[str], last_sender: str) -> Message:
        parser = MessageParser(self.date_format, self.my_name or last_sender)
        return parser.parse_message(message_lines, last_sender)

class MessageParser:
    def __init__(self, date_format: str, my_name: str):
        self.date_format = date_format
        self.my_name = my_name

    def parse_message(self, message_lines: List[str], last_sender: str) -> Message:
        first_line = TextUtils.clean_unicode(message_lines[0])
        rest_of_message = "\n".join(message_lines[1:]).strip()
        if parsed := self._try_parse_structured_message(first_line):
            timestamp_str, content = parsed
            timestamp, sender, message_content = self._parse_message_content(
                timestamp_str, content, first_line, rest_of_message
            )
        else:
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
        if line.startswith("[") and "]" in line:
            parts = line.split('] ', 1)
            if len(parts) == 2:
                return parts[0].replace('[', ''), parts[1]
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
        try:
            timestamp = datetime.strptime(timestamp_str, self.date_format)
            if content.startswith(SpecialMessages.MY_MESSAGE_PREFIX):
                sender = self.my_name
                message_content = content[3:]
            else:
                sender, message_content = content.split(': ', 1)
            if rest_of_message:
                message_content = f"{message_content}\n{rest_of_message}"
            return timestamp, sender.strip(), message_content.strip()
        except Exception:
            full_content = f"{first_line}\n{rest_of_message}" if rest_of_message else first_line
            return None, '', full_content
