import logging
from typing import Any, Callable
import functools
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Decorator function
def error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator for handling exceptions and logging errors."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            # You can customize the error handling here, e.g., re-raise the exception
            raise
    return wrapper

@contextmanager
def temporary_log_level(logger, level):
    """Temporarily change the log level of a logger."""
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)
