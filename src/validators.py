"""
Input validation utilities.
"""

from pathlib import Path
from typing import List


class ParticipantValidator:
    """Validates participant selection."""
    
    @staticmethod
    def validate(participant: str, valid_participants: List[str]) -> bool:
        """
        Validate that participant exists in list.
        
        Args:
            participant: Participant name to validate
            valid_participants: List of valid participant names
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If participant not found
        """
        if participant not in valid_participants:
            error_msg = f"\nError: Participant '{participant}' not found.\n\n"
            error_msg += "Available participants:\n"
            for i, p in enumerate(valid_participants, 1):
                error_msg += f"  {i}. {p}\n"
            error_msg += "\nPlease use one of the names listed above."
            raise ValueError(error_msg)
        return True


class UserInteraction:
    """Handles user interaction for interactive mode."""
    
    @staticmethod
    def select_participant(participants: List[str]) -> str:
        """
        Let user select their name from participants.
        
        Args:
            participants: List of participant names
            
        Returns:
            Selected participant name
        """
        print("\nParticipants found in chat:")
        for i, participant in enumerate(participants, 1):
            print(f"  {i}. {participant}")
        
        while True:
            try:
                choice = input("\nEnter number for your name: ").strip()
                index = int(choice) - 1
                
                if 0 <= index < len(participants):
                    return participants[index]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nCancelled by user.")
                raise
    
    @staticmethod
    def get_date_range() -> tuple:
        """
        Get optional date range from user.
        
        Returns:
            Tuple of (from_date_str, until_date_str)
        """
        print("\nOptional: Enter date range to filter messages")
        print("Supported formats: MM/DD/YYYY, DD.MM.YYYY, MM/DD/YY, DD.MM.YY")
        print("Leave empty to skip")
        
        from_date = input("From date (optional): ").strip()
        until_date = input("Until date (optional): ").strip()
        
        return from_date or None, until_date or None
    
    @staticmethod
    def confirm_open_browser() -> bool:
        """Ask if user wants to open files in browser."""
        response = input("\nOpen HTML files in browser? [Y/n]: ").strip().lower()
        return response != 'n'
