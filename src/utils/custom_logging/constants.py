# src/utils/custom_logging/constants.py

# Constants for magic strings
LOG_ASCTIME = "asctime"
LOG_CREATED = "created"
LOG_LEVEL = "levelname"
LOG_NAME = "name"
LOG_MESSAGE = "message"

# Detailed logging format string (for debug level)
DETAILED_LOG_FORMAT = (
    f'{{ "{LOG_ASCTIME}":"%({LOG_ASCTIME})s", "{LOG_CREATED}":%({LOG_CREATED})f, '
    f'"{LOG_LEVEL}":"%({LOG_LEVEL})s", "{LOG_NAME}":"%({LOG_NAME})s", '
    f'"{LOG_MESSAGE}":"%({LOG_MESSAGE})s" }}'
)

# Simple logging format string (for info level and above)
SIMPLE_LOG_FORMAT = f'%({LOG_ASCTIME})s - %({LOG_LEVEL})s - %({LOG_MESSAGE})s'

# Default logging configuration
DEFAULT_LOGGING_CONFIG = {
    'level': 'DEBUG',
    'ring_buffer_capacity': 100,
}
