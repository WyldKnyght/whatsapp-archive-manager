"""
Core message parsing logic for WhatsApp chat exports.
"""

import re
from datetime import datetime
from typing import List, Tuple, Optional, Set
from src.models.message import Message
from src.models.chat import Chat
from src.models.date_range import DateRange
from src.parsers.date_format_detector import DateFormatDetector
from src.parsers.sender_extractor import SenderExtractor
from src.utils.color_utils import ColorMapper
from src.utils.string_utils import StringCleaner

class MessageParser:
    """
    Parses WhatsApp chat export content into structured Message objects.
    Single Responsibility: Only parsing messages from raw text.
    """
    
    def __init__(self, platform: str, attachments_in_zip: Set[str] = None):
        """
        Initialize the message parser.
        """
        self.platform = platform
        self.attachments_in_zip = attachments_in_zip or set()
        self.date_format = None

        # General pattern supporting exported lines with AM/PM and funky unicode spaces
        # Example: [2025-08-23, 9:19:02 PM] John: message
        self.message_pattern = r"\[(.*?)\]\s*([^:]+):\s*(.*)"

    
    def parse(self, content: str, chat_name: str, own_name: str, 
              date_range: Optional[DateRange] = None) -> Tuple[Chat, int, int]:
        """
        Parse chat content into a Chat object.
        
        Args:
            content: Raw chat export content
            chat_name: Name of the chat
            own_name: Name of the current user
            date_range: Optional date range for filtering
            
        Returns:
            Tuple of (Chat object, filtered_count, total_count)
        """
        # Detect date format
        self.date_format = DateFormatDetector.detect_date_format(content, self.platform)

        # Extract senders
        senders = SenderExtractor.extract_senders(content, self.platform)

        # Generate color map
        color_mapper = ColorMapper(own_name)
        color_map = color_mapper.generate_color_map(senders)

        # Parse messages
        messages = []
        total_count = 0
        filtered_count = 0

        lines = content.split('\n')
        current_message = None

        for line in lines:
            if match := re.match(self.message_pattern, line):
                # Save previous message if exists
                if current_message:
                    if not date_range or date_range.contains(current_message.timestamp):
                        messages.append(current_message)
                        filtered_count += 1
                    total_count += 1

                # Parse new message
                timestamp_str, sender, text = match.groups()
                current_message = self._parse_message_line(timestamp_str, sender, text)

            elif current_message:
                # This is a continuation of the previous message
                current_message.text += '\n' + line

        # Don't forget the last message
        if current_message:
            if not date_range or date_range.contains(current_message.timestamp):
                messages.append(current_message)
                filtered_count += 1
            total_count += 1

        # Create Chat object
        chat = Chat(
            name=chat_name,
            messages=messages,
            sender_color_map=color_map,
            own_name=own_name,
            date_range=date_range,
            platform=self.platform
        )

        return chat, filtered_count, total_count
    
    def _parse_message_line(self, timestamp_str: str, sender: str, text: str) -> Message:
        """
        Parse a single message line.
        
        Args:
            timestamp_str: Raw timestamp string
            sender: Sender name
            text: Message text
            
        Returns:
            Message object
        """
        # Parse timestamp
        timestamp = self._parse_timestamp(timestamp_str)
        
        # Clean sender name
        sender = StringCleaner.clean_sender_name(sender)
        
        # Check for attachments
        attachment, attachment_type = self._extract_attachment(text)
        
        # Determine if system message
        is_system = self._is_system_message(text)
        
        return Message(
            timestamp=timestamp,
            sender=sender,
            text=text.strip(),
            attachment=attachment,
            attachment_type=attachment_type,
            is_system_message=is_system
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        # Remove narrow no-break space (U+202F)
        timestamp_str = timestamp_str.replace('\u202f', '').strip()
        for fmt in [
            "%Y-%m-%d, %I:%M:%S%p",  # your sample
            "%d.%m.%Y, %H:%M:%S",    # old iOS
            "%m/%d/%y, %I:%M:%S%p",  # classic US-style
            # add more as needed
        ]:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unrecognized timestamp format: {timestamp_str}")

    
    def _extract_attachment(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract attachment information from message text.
        Returns: Tuple of (attachment_filename, attachment_type)
        """
        if marker := re.search(r"<attached:\s*([A-Za-z0-9\-_. ]+\.\w+)>", text):
            filename = marker[1]
            ext = filename.split('.')[-1].lower()
            # Map extension to type
            if ext in ["jpg", "jpeg", "png", "gif", "webp", "heic"]:
                att_type = "image"
            elif ext in ["opus", "mp3", "m4a", "ogg", "wav"]:
                att_type = "audio"
            elif ext in ["mp4", "mov", "avi", "webm"]:
                att_type = "video"
            else:
                att_type = "document"
            # Remove the attached tag from text for clean rendering
            # This ensures "<attached: ...>" does not appear in chat output
            text = re.sub(r"<attached:[^>]+>", "", text).strip()
            return filename, att_type

        # Old fallback patterns (your previous code) for legacy style:
        attachment_indicators = {
            'image': r'(IMG[-_]\d+\.\w+|IMAGE[-_]\d+\.\w+|\w+\.jpg|\w+\.png|\w+\.jpeg)',
            'video': r'(VID[-_]\d+\.\w+|VIDEO[-_]\d+\.\w+|\w+\.mp4|\w+\.mov)',
            'audio': r'(AUD[-_]\d+\.\w+|AUDIO[-_]\d+\.\w+|\w+\.opus|\w+\.mp3)',
            'document': r'(\w+\.pdf|\w+\.docx?|\w+\.xlsx?)',
        }

        for att_type, pattern in attachment_indicators.items():
            if match := re.search(pattern, text, re.IGNORECASE):
                filename = match[1]
                if filename in self.attachments_in_zip:
                    return filename, att_type

        return None, None

    
    def _is_system_message(self, text: str) -> bool:
        """Check if message is a system message."""
        system_patterns = [
            'Messages and calls are end-to-end encrypted',
            'Security code changed',
            'created group',
            'changed the subject',
            'changed this group',
            'left',
            'added',
            'removed',
            'changed the group description',
        ]
        
        return any(pattern in text for pattern in system_patterns)
