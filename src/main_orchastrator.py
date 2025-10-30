# src/main_orchastrator.py

from pathlib import Path
from typing import List, Set
from src.modules.message_extractor import MessageExtractor
from src.modules.message_grouper import MessageGrouper
from src.modules.file_manager import FileManager
from src.modules.message_parser import MessageParser
from src.modules.html_generator import HTMLGenerator
from src.modules.media_handler import MediaHandler
from src.data_models.chat_metadata import ChatMetadata
from src.data_models.message import Message
from src.configuration_and_enums.format_detector import FormatDetector, WhatsAppFormat

class WhatsAppChatConverter:
    """
    Main class that orchestrates the conversion process.
    Uses dependency injection for all major components.
    """
    def __init__(
        self,
        message_extractor: MessageExtractor = None,
        message_grouper: MessageGrouper = None,
        file_manager: FileManager = None
    ):
        self.message_extractor = message_extractor or MessageExtractor()
        self.message_grouper = message_grouper or MessageGrouper()
        self.file_manager = file_manager or FileManager()

    def convert_chatfile_to_html(self, chat_txt_file: Path, output_path: Path = None) -> Path:
        # Detect encoding and format
        encoding, _ = FormatDetector.detect_encoding(str(chat_txt_file))
        whatsapp_format, confidence, _ = FormatDetector.detect_format(str(chat_txt_file), encoding)
        print(f"Detected format: {whatsapp_format.value} (confidence: {confidence:.1%})")

        if whatsapp_format == WhatsAppFormat.UNKNOWN:
            raise ValueError("Could not detect WhatsApp format in chat file")

        # Get format info
        format_info = FormatDetector.get_format_info(whatsapp_format)

        # Read lines
        lines = chat_txt_file.read_text(encoding=encoding).splitlines()

        # Extract metadata using the detected format
        chat_metadata = self._extract_chat_metadata(lines, format_info)

        # Create parser with detected format
        message_parser = MessageParser(
            chat_metadata.date_format,
            chat_metadata.my_name
        )

        # Parse messages
        messages = self._parse_all_messages(lines, message_parser)

        # Generate HTML
        media_handler = MediaHandler(chat_txt_file.parent)
        html_generator = HTMLGenerator()
        html_content = html_generator.generate_html(messages, chat_metadata, media_handler)

        # Save output
        if output_path is None:
            version = self.file_manager.get_next_version_number(chat_txt_file.parent, chat_txt_file.stem)
            output_path = chat_txt_file.parent / f"{chat_txt_file.stem}_v{version}.html"
        output_path.write_text(html_content, encoding='utf-8')
        return output_path

    def _extract_chat_metadata(self, lines: List[str], format_info) -> ChatMetadata:
        """Extract metadata using the detected format info."""
        date_format = f"{format_info.date_format} {format_info.time_format}"
        participant_names = self.message_extractor.extract_participant_names(lines)
        my_name = self._determine_my_name(participant_names)
        return ChatMetadata(
            participant_names=participant_names,
            date_format=date_format,
            my_name=my_name
        )

    @staticmethod
    def _determine_my_name(participant_names: Set[str]) -> str:
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
