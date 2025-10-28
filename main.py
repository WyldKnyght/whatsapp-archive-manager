from pathlib import Path
from src.utils.custom_logging.setup_logging import setup_logging
from src.main_orchastrator import WhatsAppChatConverter
from src.modules.file_manager import FileManager

import zipfile
import tempfile
from tkinter import Tk, filedialog, messagebox

setup_logging()

def main():
    Tk().withdraw()  # Hide root window

    # Ask user to select a WhatsApp ZIP export file
    zip_path = filedialog.askopenfilename(
        filetypes=[("WhatsApp ZIP files", "*.zip")],
        title="Select your WhatsApp ZIP export"
    )
    if not zip_path:
        messagebox.showinfo("No Selection", "No ZIP file selected. Exiting.")
        return

    zip_path = Path(zip_path)
    temp_dir = tempfile.TemporaryDirectory(dir=zip_path.parent)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir.name)
    except Exception as ex:
        messagebox.showerror("Error", f"Problem opening ZIP file:\n{ex}")
        temp_dir.cleanup()
        return

    # Find possible chat TXT files in the extracted folder
    chat_files = [
        f for f in Path(temp_dir.name).rglob("*.txt")
        if "_chat" in f.name or "WhatsApp Chat" in f.name
    ]
    if not chat_files:
        messagebox.showerror("Error", "No chat text file found in the ZIP!")
        temp_dir.cleanup()
        return

    selected_chat_file = chat_files[0]  # Take the first if multiple

    # Convert to HTML
    converter = WhatsAppChatConverter()
    try:
        output_file = converter.convert_chatfile_to_html(
            selected_chat_file,
            output_path=zip_path.parent / f"{selected_chat_file.stem}.html",
        )
        messagebox.showinfo("Success", f"✅ HTML file created:\n{output_file}")
    except Exception as e:
        import traceback
        traceback_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        messagebox.showerror("Error", f"❌ Error converting chat:\n{e}\n\nDetails:\n{traceback_str}")

    temp_dir.cleanup()

if __name__ == "__main__":
    main()
