"""
Main chat export orchestrator.
Coordinates all components following Separation of Concerns.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple
from src.models.chat import Chat
from src.models.date_range import DateRange
from src.parsers.message_parser import MessageParser
from src.parsers.sender_extractor import SenderExtractor
from src.parsers.date_format_detector import DateFormatDetector
from src.renderers.html_renderer import HTMLRenderer
from src.io.zip_handler import ZipHandler
from src.utils.date_utils import DateParser, DateValidator
from src.utils.path_utils import PathParser


class ChatExportOrchestrator:
    """
    Orchestrates the chat export process.
    Single Responsibility: Coordinate the export workflow.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, zip_path: Path, output_dir: Optional[Path] = None):
        """
        Initialize chat export orchestrator.
        
        Args:
            zip_path: Path to WhatsApp ZIP export
            output_dir: Optional output directory
        """
        self.zip_path = Path(zip_path)
        self.zip_handler = ZipHandler(self.zip_path)

        # Set up output directory
        zip_stem = self.zip_path.stem
        self.output_dir = Path(output_dir) / zip_stem if output_dir else Path(zip_stem)
        self.media_dir = self.output_dir / "media"

        # Will be set during processing
        self.platform: Optional[str] = None
        self.has_media: bool = False
        self.chat_file: Optional[str] = None
        self.media_files: set = set()
    
    def setup(self) -> None:
        """
        Set up the export environment.
        Detects platform, finds chat file, and prepares directories.
        """
        # Find chat file and detect platform
        self.chat_file, is_ios, self.media_files = self.zip_handler.find_chat_file()
        self.platform = 'ios' if is_ios else 'android'
        self.has_media = len(self.media_files) > 0
        
        print(f"Detected {self.platform.upper()} export with "
              f"{'media' if self.has_media else 'no media'}")
        print(f"Chat file: {self.chat_file}")
        
        # Prepare output directories
        self._prepare_output_directory()
    
    def _prepare_output_directory(self) -> None:
        """Prepare output directory (clean if exists, create fresh)."""
        if self.output_dir.exists():
            print(f"Cleaning existing directory: {self.output_dir}")
            shutil.rmtree(self.output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.has_media:
            self.media_dir.mkdir(exist_ok=True)
    
    def get_participants(self) -> list:
        """
        Get list of chat participants.
        
        Returns:
            Sorted list of participant names
        """
        content = self.zip_handler.read_chat_content(self.chat_file)
        return SenderExtractor.extract_senders(content, self.platform)
    
    def export(self, own_name: str, 
               from_date: Optional[str] = None,
               until_date: Optional[str] = None) -> Tuple[Chat, int, int]:
        """
        Export chat with specified parameters.
        
        Args:
            own_name: Name of the current user
            from_date: Optional start date (string)
            until_date: Optional end date (string)
            
        Returns:
            Tuple of (Chat object, filtered_count, total_count)
        """
        start_time = time.time()
        
        # Parse dates
        date_range = self._create_date_range(from_date, until_date)
        
        # Read chat content
        print("Reading chat content...")
        content = self.zip_handler.read_chat_content(self.chat_file)
        
        # Parse messages
        print("Parsing messages...")
        parser = MessageParser(self.platform, self.media_files)
        chat, filtered_count, total_count = parser.parse(
            content,
            chat_name=self.zip_path.name,
            own_name=own_name,
            date_range=date_range
        )
        
        # Report filtering results
        if date_range and date_range.is_filtered():
            print(f"{filtered_count} of {total_count} messages match date filter")
            if filtered_count == 0:
                raise ValueError("No messages in specified date range")
        
        print(f"Exporting {len(chat.messages)} messages...")
        
        # Render HTML
        print("Rendering HTML...")
        renderer = HTMLRenderer(self.output_dir, self.has_media)
        attachments_to_extract = renderer.render(chat)
        
        # Extract media files
        if self.has_media and attachments_to_extract:
            print(f"Extracting {len(attachments_to_extract)} media files...")
            self.zip_handler.extract_files(attachments_to_extract, self.media_dir)
        
        # Clean up empty media directory
        if self.has_media and not any(self.media_dir.iterdir()):
            self.media_dir.rmdir()
        
        elapsed = time.time() - start_time
        print(f"Export completed in {elapsed:.2f} seconds")
        
        return chat, filtered_count, total_count
    
    def _create_date_range(self, from_date: Optional[str], 
                          until_date: Optional[str]) -> Optional[DateRange]:
        """
        Create DateRange object from date strings.
        
        Args:
            from_date: Start date string
            until_date: End date string
            
        Returns:
            DateRange object or None if no dates specified
        """
        if not from_date and not until_date:
            return None
        
        parsed_from = DateParser.parse_date(from_date) if from_date else None
        parsed_until = DateParser.parse_date(until_date) if until_date else None
        
        DateValidator.validate_range(parsed_from, parsed_until)
        
        return DateRange(parsed_from, parsed_until)
    
    def get_output_files(self) -> list:
        """Get list of generated output files."""
        files = []
        files.extend(iter(self.output_dir.glob("*.html")))
        return sorted(files)
