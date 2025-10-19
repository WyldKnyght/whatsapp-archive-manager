from pathlib import Path
from typing import List, Set
from src.modules.date_format_detector import DateFormatDetector
from src.modules.message_extractor import MessageExtractor
from src.modules.message_grouper import MessageGrouper
from src.modules.file_manager import FileManager
from src.modules.message_parser import MessageParser
from src.modules.html_generator import HTMLGenerator
from src.modules.media_handler import MediaHandler
from data_models.chat_metadata import ChatMetadata
from src.data_models.message import Message

class WhatsAppChatConverter:
    """
    Main class that orchestrates the conversion process
    Uses dependency injection for all major components
    """

    def __init__(
        self,
        date_detector: DateFormatDetector = None,
        message_extractor: MessageExtractor = None,
        message_grouper: MessageGrouper = None,
        file_manager: FileManager = None
    ):
        self.date_detector = date_detector or DateFormatDetector()
        self.message_extractor = message_extractor or MessageExtractor()
        self.message_grouper = message_grouper or MessageGrouper()
        self.file_manager = file_manager or FileManager()

    def convert_folder_to_html(self, folder_path: Path, output_path: Path = None) -> Path:
        """
        Convert a WhatsApp chat export folder to HTML

        Args:
            folder_path: Path to folder containing chat export
            output_path: Optional path for output file

        Returns:
            Path to generated HTML file
        """
        # Read chat file
        lines = self.file_manager.read_chat_file(folder_path)

        # Extract metadata
        chat_metadata = self._extract_chat_metadata(lines)

        # Parse messages
        message_parser = MessageParser(chat_metadata.date_format, chat_metadata.my_name)
        messages = self._parse_all_messages(lines, message_parser)

        # Generate HTML
        media_handler = MediaHandler(folder_path)
        html_generator = HTMLGenerator()
        html_content = html_generator.generate_html(messages, chat_metadata, media_handler)

        # Write output file
        if output_path is None:
            version = self.file_manager.get_next_version_number(
                folder_path.parent,
                folder_path.name
            )
            output_path = folder_path.parent / f"{folder_path.name}_v{version}.html"

        output_path.write_text(html_content, encoding='utf-8')

        return output_path

    def _extract_chat_metadata(self, lines: List[str]) -> ChatMetadata:
        """Extract metadata from chat lines"""
        timestamps = self.message_extractor.extract_timestamps(lines)
        date_format = self.date_detector.detect_format(timestamps)

        if not date_format:
            raise ValueError("Could not detect date format in chat file")

        participant_names = self.message_extractor.extract_participant_names(lines)

        # Determine "my" name (prompt user or use logic)
        my_name = self._determine_my_name(participant_names)

        return ChatMetadata(
            participant_names=participant_names,
            date_format=date_format,
            my_name=my_name
        )

    @staticmethod
    def _determine_my_name(participant_names: Set[str]) -> str:
        """Determine which participant is 'me' """
        if len(participant_names) == 1:
            return list(participant_names)[0]

        if len(participant_names) == 2:
            print("\nDetected participants:")
            for i, name in enumerate(sorted(participant_names), 1):
                print(f"{i}. {name}")

            choice = input("\nWhich one is you? (enter number): ")
            try:
                index = int(choice) - 1
                return sorted(participant_names)[index]
            except (ValueError, IndexError):
                return sorted(participant_names)[0]

        return sorted(participant_names)[0]

    def _parse_all_messages(self, lines: List[str], message_parser: MessageParser) -> List[Message]:
        """Parse all messages from chat lines"""
        message_start_lines = self.message_grouper.get_message_start_lines(lines)
        messages = []
        last_sender = ""

        for i in range(len(message_start_lines)):
            start = message_start_lines[i]
            end = message_start_lines[i + 1] if i + 1 < len(message_start_lines) else len(lines)

            message_lines = lines[start:end]
            message = message_parser.parse_message(message_lines, last_sender)
            messages.append(message)

            if message.sender:
                last_sender = message.sender

        return messages

