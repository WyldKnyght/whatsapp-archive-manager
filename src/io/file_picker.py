"""
File picker UI handling.
"""

import sys
import os
from pathlib import Path
from typing import Optional


class FilePicker:
    """
    Handles file picker dialogs.
    Single Responsibility: Only file selection UI.
    """
    
    @staticmethod
    def pick_zip_file() -> Optional[Path]:
        """
        Open file picker dialog to select a ZIP file.
        
        Returns:
            Path to selected file, or None if cancelled
        """
        # Try Windows picker first if on Windows
        if sys.platform == 'win32':
            result = FilePicker._windows_picker()
            if result:
                return Path(result)
        
        # Fall back to tkinter for all other platforms
        result = FilePicker._tkinter_picker()
        return Path(result) if result else None
    
    @staticmethod
    def _windows_picker() -> Optional[str]:
        """Windows native file picker using pywin32."""
        try:
            import win32ui
            import win32con

            file_filter = "ZIP Files (*.zip)|*.zip|All Files (*.*)|*.*||"
            dlg = win32ui.CreateFileDialog(1, None, None, 0, file_filter)
            dlg.SetOFNTitle("Select WhatsApp Chat Export ZIP File")
            dlg.SetOFNInitialDir(os.path.expanduser("~"))

            return dlg.GetPathName() if dlg.DoModal() == 1 else None
        except ImportError:
            return None
    
    @staticmethod
    def _tkinter_picker() -> Optional[str]:
        """Cross-platform file picker using tkinter."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            file_path = filedialog.askopenfilename(
                title="Select WhatsApp Chat Export ZIP File",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
            )
            
            root.destroy()
            return file_path or None
        except Exception as e:
            print(f"Tkinter not available: {e}")
            return None
