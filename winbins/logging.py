"""
Logging utilities for WinBins.
Provides consistent logging across all modules.
"""

import logging
import sys
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class WinBinsLogger:
    """Custom logger for WinBins with colored output support."""

    COLORS = {
        LogLevel.DEBUG: "\033[36m",    # Cyan
        LogLevel.INFO: "\033[37m",     # White
        LogLevel.WARNING: "\033[33m",  # Yellow
        LogLevel.ERROR: "\033[31m",    # Red
        LogLevel.SUCCESS: "\033[32m",  # Green
    }
    RESET = "\033[0m"

    def __init__(self, name: str = "WinBins", verbose: bool = False,
                 use_colors: bool = True, log_file: Optional[str] = None):
        self.name = name
        self.verbose = verbose
        self.use_colors = use_colors and sys.stdout.isatty()
        self.log_file = log_file

        # Setup file logging if specified
        self._file_handler = None
        if log_file:
            self._setup_file_logging(log_file)

    def _setup_file_logging(self, log_file: str) -> None:
        """Setup file logging."""
        self._file_handler = logging.FileHandler(log_file)
        self._file_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        )

    def _format_message(self, msg: str, level: LogLevel) -> str:
        """Format message with optional color."""
        prefix = f"[{level.value}]"
        if self.use_colors:
            color = self.COLORS.get(level, "")
            return f"{color}{prefix}{self.RESET} {msg}"
        return f"{prefix} {msg}"

    def log(self, msg: str, level: LogLevel = LogLevel.INFO) -> None:
        """Log a message."""
        if level == LogLevel.DEBUG and not self.verbose:
            return

        formatted = self._format_message(msg, level)
        print(formatted)

        if self._file_handler:
            # Write uncolored version to file
            self._file_handler.emit(
                logging.LogRecord(
                    self.name, logging.INFO, "", 0,
                    f"[{level.value}] {msg}", None, None
                )
            )

    def debug(self, msg: str) -> None:
        """Log debug message."""
        self.log(msg, LogLevel.DEBUG)

    def info(self, msg: str) -> None:
        """Log info message."""
        self.log(msg, LogLevel.INFO)

    def warning(self, msg: str) -> None:
        """Log warning message."""
        self.log(msg, LogLevel.WARNING)

    def error(self, msg: str) -> None:
        """Log error message."""
        self.log(msg, LogLevel.ERROR)

    def success(self, msg: str) -> None:
        """Log success message."""
        self.log(msg, LogLevel.SUCCESS)


# Default logger instance
_default_logger: Optional[WinBinsLogger] = None


def get_logger(verbose: bool = False, **kwargs) -> WinBinsLogger:
    """Get or create the default logger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = WinBinsLogger(verbose=verbose, **kwargs)
    return _default_logger


def set_logger(logger: WinBinsLogger) -> None:
    """Set a custom logger as the default."""
    global _default_logger
    _default_logger = logger
