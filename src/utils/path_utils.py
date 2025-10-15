"""
Path parsing and file system utilities.
Follows Single Responsibility Principle - only handles path operations.
"""

import os
from pathlib import Path, PureWindowsPath, PurePosixPath


class PathParser:
    """Handles parsing and normalization of file paths."""
    
    @staticmethod
    def parse_path(path_str: str) -> Path:
        """
        Parse a path string safely, handling both Windows and Unix styles.
        Returns a pathlib.Path object normalized to the current OS.
        
        Args:
            path_str: Path string to parse
            
        Returns:
            Path object normalized for current OS
        """
        path_str = path_str.strip()
        
        # Strip quotes from the path string if present
        if (path_str.startswith('"') and path_str.endswith('"')) or \
           (path_str.startswith("'") and path_str.endswith("'")):
            path_str = path_str[1:-1]
        
        # Detect if it's a Windows path (contains backslashes or drive letter)
        is_windows_path = '\\' in path_str or (len(path_str) > 1 and path_str[1] == ':')
        
        if is_windows_path:
            # Parse as Windows path first
            win_path = PureWindowsPath(path_str)
            # Convert to current OS path
            return Path(win_path.as_posix())
        else:
            # Parse as Posix path
            posix_path = PurePosixPath(path_str)
            return Path(str(posix_path))
    
    @staticmethod
    def ensure_directory_exists(directory: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Path to directory
        """
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Convert a filename to a safe version by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        safe_name = filename
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        return safe_name
