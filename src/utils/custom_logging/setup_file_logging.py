import os
import logging
from datetime import datetime
from .handlers import ConditionalFileHandler

def default_log_dir():
    # Use current directory or explicitly set environment variable
    base_dir = os.getenv('LOG_BASEDIR', os.getcwd())
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def setup_file_logging():
    log_dir = default_log_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'update_log_{timestamp}.log')

    file_handler = ConditionalFileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(funcName)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    return file_handler


def get_update_logger():
    logger = logging.getLogger('update_logger')
    logger.setLevel(logging.INFO)

    # Only add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(filename)s:%(funcName)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def enable_file_logging(file_handler):
    file_handler.enable_file_logging()
