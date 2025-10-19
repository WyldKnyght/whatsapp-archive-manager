from pathlib import Path
from utils.custom_logging.setup_logging import setup_logging

setup_logging()

from src.main_orchastrator import WhatsAppChatConverter
from src.modules.file_manager import FileManager

def main():
    """Main entry point for the script"""
    script_dir = Path(__file__).parent

    # Find available chat folders
    file_manager = FileManager()
    available_folders = file_manager.find_chat_folders(script_dir)

    if not available_folders:
        print("No chat folders found in the current directory.")
        return

    # Display folders and get user selection
    print("Available chat folders:")
    for i, folder in enumerate(available_folders, 1):
        print(f"{i}. {folder.name}")

    choice = input("\nSelect a folder number to convert: ")
    try:
        folder_index = int(choice) - 1
        selected_folder = available_folders[folder_index]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # Convert to HTML
    converter = WhatsAppChatConverter()

    try:
        output_file = converter.convert_folder_to_html(selected_folder)
        print(f"\n✅ Success! HTML file created: {output_file.name}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
