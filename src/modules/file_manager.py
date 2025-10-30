# /src/modules/file_manager.py
from pathlib import Path
from typing import List, Optional


class ChatFileReaderInterface:
    """Abstract base for chat file readers."""

    def read_chat_file(self, folder_path: Path) -> List[str]:
        raise NotImplementedError


class LocalChatFileReader(ChatFileReaderInterface):
    """Reads chat files from local filesystem using patterns."""

    def __init__(self, patterns: Optional[List[str]] = None):
        # Allow custom filename patterns for extension/Open/Closed principle
        self.patterns = patterns

    def read_chat_file(self, folder_path: Path) -> List[str]:
        patterns = self.patterns or ["_chat.txt", f"{folder_path.name}.txt"]
        for pat in patterns:
            chat_file = folder_path / pat
            if chat_file.exists():
                return chat_file.read_text(encoding='utf-8').splitlines()
        raise FileNotFoundError(f"No chat file found in {folder_path}")


class FileManager:
    """Responsible for file system operations"""

    @staticmethod
    def get_next_version_number(base_path: Path, base_name: str) -> int:
        """Get the next available version number for output file"""
        version = 0
        while (base_path / f"{base_name}_v{version}.html").exists():
            version += 1
        return version

    @staticmethod
    def find_chat_folders(parent_directory: Path) -> List[Path]:
        """Find all potential chat export folders"""
        return [
            folder for folder in parent_directory.iterdir()
            if folder.is_dir() and not folder.name.startswith('.')
        ]

    @staticmethod
    def read_chat_file(folder_path: Path, patterns: Optional[List[str]] = None) -> List[str]:
        """Delegate reading chat file to LocalChatFileReader for extension/interface use"""
        reader = LocalChatFileReader(patterns)
        return reader.read_chat_file(folder_path)
