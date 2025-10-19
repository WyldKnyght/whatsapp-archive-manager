
from pathlib import Path
from typing import List

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
    def read_chat_file(folder_path: Path) -> List[str]:
        """Read chat text file from folder"""
        # Try _chat.txt (iOS) first
        chat_file = folder_path / "_chat.txt"
        if chat_file.exists():
            return chat_file.read_text(encoding='utf-8').splitlines()

        # Try folder_name.txt (Android)
        chat_file = folder_path / f"{folder_path.name}.txt"
        if chat_file.exists():
            return chat_file.read_text(encoding='utf-8').splitlines()

        raise FileNotFoundError(f"No chat file found in {folder_path}")

