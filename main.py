"""
Main entry point for WhatsApp chat archive manager tool.
Follows Separation of Concerns - only handles workflow.
"""

import sys
import webbrowser
import traceback
from src.chat_export import ChatExportOrchestrator
from src.io.file_picker import FilePicker
from src.validators import UserInteraction

VERSION = "1.0.0"


def run_interactive():
    """
    Run the tool in interactive mode with user prompts.
    """
    print(f"Welcome to WhatsApp Archive Manager v{VERSION}")
    print("=" * 50)
    print("Select WhatsApp chat export ZIP file\n")

    try:
        return interactive_workflow()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        print(traceback.format_exc())
        return False


def interactive_workflow():
    # Get ZIP file (uses Windows picker or Tkinter cross-platform GUI)
    zip_path = FilePicker.pick_zip_file()
    if not zip_path:
        print("No file selected. Exiting.")
        return False

    print(f"\nProcessing: {zip_path}")
    # Initialize orchestrator (output directory defaults to None)
    orchestrator = ChatExportOrchestrator(zip_path)
    # Setup (detect platform, prepare directories)
    orchestrator.setup()
    # Get participants (usernames found in chat file)
    participants = orchestrator.get_participants()
    # Let user select their name (prompted selection in terminal)
    own_name = UserInteraction.select_participant(participants)
    # Get optional date range (prompted selection in terminal)
    from_date, until_date = UserInteraction.get_date_range()
    # Perform export
    chat, filtered_count, total_count = orchestrator.export(
        own_name=own_name,
        from_date=from_date,
        until_date=until_date
    )
    # Show results
    output_files = orchestrator.get_output_files()
    print(f"\nGenerated files:")
    for file_path in output_files:
        print(f"  - {file_path.absolute()}")
    # Optional: Ask to open in browser
    if UserInteraction.confirm_open_browser():
        for file_path in reversed(output_files):
            webbrowser.open(f"file://{file_path.absolute().as_posix()}")
    return True


def main():
    """Main entry point."""
    success = run_interactive()
    if not success:
        input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
