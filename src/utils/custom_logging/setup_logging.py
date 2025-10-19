# src/utils/custom_logging/setup_logging.py
import logging
import logging.config
import os
from typing import Any, Dict, Optional
from .constants import DEFAULT_LOGGING_CONFIG, DETAILED_LOG_FORMAT, SIMPLE_LOG_FORMAT
from utils.custom_logging.handlers import DetailedRichHandler

logger = logging.getLogger(__name__)

def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Set up logging configuration.

    Args:
        config (Optional[Dict[str, Any]]): Custom logging configuration. 
                                            If None, DEFAULT_LOGGING_CONFIG is used.

    Raises:
        ValueError: If the provided configuration is invalid.
    """
    if config is None:
        config = DEFAULT_LOGGING_CONFIG.copy()
    else:
        # Ensure all required keys are present
        required_keys = ['level', 'ring_buffer_capacity']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")

    # Dynamically set logging level from environment variables
    env_log_level = os.getenv("LOG_LEVEL", config['level'].upper())
    try:
        logging.getLevelName(env_log_level)
    except ValueError as e:
        raise ValueError(f"Invalid log level: {env_log_level}") from e

    config['level'] = env_log_level

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {'format': DETAILED_LOG_FORMAT},
            'simple': {'format': SIMPLE_LOG_FORMAT},
        },
        'handlers': {
            'console': {
                '()': DetailedRichHandler,
                'level': config['level'],
            },
            'ring_buffer': {
                'class': 'utils.custom_logging.handlers.RingBuffer',
                'capacity': config['ring_buffer_capacity'],
                'level': config['level'],
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'ring_buffer'],
                'level': config['level'],
            },
        },
    }

    try:
        logging.config.dictConfig(logging_config)
    except (ValueError, TypeError, AttributeError) as e:
        raise ValueError(f"Invalid logging configuration: {str(e)}") from e

    # Suppress unnecessary logging from other libraries
    libraries_to_suppress = ["urllib3", "httpx", "diffusers", "torch"]
    for library in libraries_to_suppress:
        logging.getLogger(library).setLevel(logging.ERROR)

    file_handler = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': 'app.log',
        'maxBytes': 10485760,  # 10MB
        'backupCount': 5,
        'formatter': 'detailed',
    }
    logging_config['handlers']['file'] = file_handler
    logging_config['loggers']['']['handlers'].append('file')

    logger.info("Logging setup completed successfully")
