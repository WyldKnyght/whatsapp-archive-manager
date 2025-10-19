# 🗂️ Overview of Custom Logging Code

### Files & Structure

- **setup_logging.py**
  - Main logging configuration setup (`setup_logging`)
  - Uses config dict (default or custom)
  - Dynamically sets log level from env
  - Adds console, ring buffer, and (optionally) file handlers
  - Uses custom `DetailedRichHandler` for colored console output

- **setup_file_logging.py**
  - Adds a `ConditionalFileHandler` for dynamic file logging
  - `get_update_logger()` returns a logger with console handler
  - `enable_file_logging()` switches on file logging (records buffered logs to file)

- **handlers.py**
  - **RingBuffer**: Keeps last N log records in memory (useful for quick access/UI)
  - **DetailedRichHandler**: Pretty, colored logs to console using Rich library
  - **ConditionalFileHandler**: Buffers logs, only writes to file when enabled
  - All handlers use formats from constants

- **decorators.py**
  - **@error_handler** decorator: wraps a function to catch exceptions and log them gracefully
  - **temporary_log_level**: context manager for temporarily setting a logger's level

- **constants.py**
  - Centralizes all log-related magic strings and format patterns
  - Two formats:
    - **DETAILED_LOG_FORMAT** (JSON, used for debug)
    - **SIMPLE_LOG_FORMAT** (plain text, for info and above)
  - `DEFAULT_LOGGING_CONFIG`

***

## 🎯 Key Features & Patterns

- **SOLID/Clean Code**:
  - **Single Responsibility**: Custom handlers in their own classes. Constants and config separated.
  - **DRY**: Log formats and strings in `constants.py`. No repeated format strings.
  - **Open/Closed**: Extendable—add new handlers or formats easily.
  - **Minimal Arguments**: Handlers and setup functions have clean signatures.
  - **Descriptive Names**: `ConditionalFileHandler`, `RingBuffer`, etc.

- **Rich Integration**:
  - Uses Rich `Console` for beautiful, high-contrast logs.
  - Theme allows custom colors for tracebacks and value borders.

- **Ring Buffer**:
  - Efficient for storing N in-memory logs for reviewing recent events in GUI apps.

- **Conditional File Logging**:
  - Buffers logs until explicitly enabled.
  - Prevents unnecessary file writes until absolutely needed.

- **Config-Driven**:
  - Logging configuration via dict (supports overrides and environment variables).

- **Exception Logging Decorator**:
  - `@error_handler` will catch/log any exceptions, with stack traces (via `exc_info=True`).
  - Robust for wrapping any utility functions.

- **Context Manager**:
  - Temporarily elevates or reduces log verbosity (good for troubleshooting one-off blocks).

- **Suppression of External Loggers**:
  - (Found in setup) Suppresses noisy third-party library output unless set to ERROR.

***

## 📝 Example (How to Use)

```python
from utils.custom_logging.setup_logging import setup_logging
setup_logging()
import logging

logging.info("Standard log")
logging.debug("This will be colored and in debug format")
```

**Get and use a ring buffer:**
```python
import logging
buffer = logging.getLogger().handlers[1]  # assuming ring buffer is handler 1
recent_logs = buffer.get()  # get last N log messages as list
```

**Enable file logging:**
```python
from setup_file_logging import setup_file_logging, enable_file_logging

file_handler = setup_file_logging()
logger = logging.getLogger('update_logger')
logger.addHandler(file_handler)

# Start logging to file
enable_file_logging(file_handler)
```

***

## ⚡ Best-Practice Highlights

- **Log format strings are centralized** → Easy to change everywhere at once.
- **Buffered file handler** is rare; helps avoid premature file writes, great for GUI apps.
- **Rich handler** for eye-friendly logs.
- **Decorator for error logging** means no duplicate try/except/log code.
- **Ring buffer** is optimal for dashboards or in-app log viewers.

***

## 🟢 Suggestions/Next Steps

- 🔄 If needed, add support for custom log filters (e.g., only error logs in file handler).
- 🧪 Add tests for decorators/handlers (trivial now due to clear class separation).
- 📁 Add log file rotation support in file handler for long-running applications.
- 🪧 Document usage in `README.md` or inline at the top of each script.

