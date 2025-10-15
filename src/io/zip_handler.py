"""
ZIP file handling operations.
"""

import zipfile
import shutil
from pathlib import Path
from typing import List, Set, Tuple
import difflib


class ZipHandler:
    """
    Handles ZIP file operations.
    Single Responsibility: Only ZIP file handling.
    """
    
    def __init__(self, zip_path: Path):
        """
        Initialize ZIP handler.
        
        Args:
            zip_path: Path to ZIP file
        """
        self.zip_path = Path(zip_path)
        self._validate_zip()
    
    def _validate_zip(self) -> None:
        """Validate that the ZIP file exists and is valid."""
        if not self.zip_path.exists():
            raise FileNotFoundError(f"Could not find file: {self.zip_path}")

        if self.zip_path.suffix.lower() != '.zip':
            raise ValueError(f"File is not a ZIP file: {self.zip_path}")

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                # Test if it's a valid ZIP
                zf.testzip()
        except zipfile.BadZipFile as e:
            raise ValueError(f"File is not a valid ZIP file: {self.zip_path}") from e
    
    def get_file_list(self) -> List[str]:
        """
        Get list of all files in the ZIP.
        
        Returns:
            List of filenames
        """
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            return zf.namelist()
    
    def find_chat_file(self) -> Tuple[str, bool, Set[str]]:
        """
        Find the chat text file and detect platform.
        
        Returns:
            Tuple of (chat_filename, is_ios, set_of_media_files)
        """
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            all_files = zf.namelist()

            # Find text files
            txt_files = [f for f in all_files if f.lower().endswith('.txt')]

            if not txt_files:
                raise FileNotFoundError("No text files found in ZIP archive")

            # Check for iOS format
            if '_chat.txt' in txt_files:
                chat_file = '_chat.txt'
                is_ios = True
            else:
                # Android format - find most likely chat file
                zip_stem = self.zip_path.stem
                chat_file = self._find_most_similar(f"{zip_stem}.txt", txt_files)
                is_ios = False

            # Get media files (all non-chat files)
            media_files = {f for f in all_files if f != chat_file}

            return chat_file, is_ios, media_files
    
    def read_chat_content(self, chat_file: str) -> str:
        """
        Read chat text file content.
        
        Args:
            chat_file: Name of chat file in ZIP
            
        Returns:
            Chat content as string
        """
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            with zf.open(chat_file) as f:
                return f.read().decode('utf-8')
    
    def extract_files(self, file_list: Set[str], output_dir: Path) -> None:
        """
        Extract specific files from ZIP.
        
        Args:
            file_list: Set of filenames to extract
            output_dir: Output directory
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            for filename in file_list:
                try:
                    zf.extract(filename, output_dir)
                except KeyError:
                    print(f"Warning: File {filename} not found in ZIP")
    
    @staticmethod
    def _find_most_similar(target: str, candidates: List[str]) -> str:
        """
        Find most similar string from candidates.
        
        Args:
            target: Target string
            candidates: List of candidate strings
            
        Returns:
            Most similar string
        """
        if not candidates:
            raise ValueError("No candidates provided")
        
        return max(candidates, key=lambda c: 
                  difflib.SequenceMatcher(None, target, c).ratio())

