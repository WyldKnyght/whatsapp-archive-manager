# src/configuration_and_enums/special_messages.py

class SpecialMessages:
    """Configuration for special message indicators."""

    # Indicates a message with no content (such as some calls)
    NULL_MESSAGE = 'null'

    # Indicates a file is attached to the message
    FILE_ATTACHED = '(file attached)'

    # Indicates a missed call event
    MISSED_CALL = 'Missed'

    # Prefix for messages sent by "me"
    MY_MESSAGE_PREFIX = '.:'
