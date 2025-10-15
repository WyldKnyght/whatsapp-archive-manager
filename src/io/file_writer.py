"""
File writing operations.
"""

import os
from pathlib import Path
from typing import Union


class FileWriter:
    """
    Handles file writing operations.
    Single Responsibility: Only file writing.
    """
    
    @staticmethod
    def write_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding (default: utf-8)
        """
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def write_binary(file_path: Union[str, Path], content: bytes) -> None:
        """
        Write binary content to a file.
        
        Args:
            file_path: Path to file
            content: Binary content to write
        """
        file_path = Path(file_path)
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(content)
