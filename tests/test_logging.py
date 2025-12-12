"""
Tests for the logging module.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from winbins.logging import (
    WinBinsLogger,
    LogLevel,
    get_logger,
    set_logger,
)


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_all_levels_exist(self):
        """Test all log levels are defined."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "SUCCESS"]
        for level in levels:
            assert LogLevel[level] is not None


class TestWinBinsLogger:
    """Tests for WinBinsLogger class."""

    def test_init_defaults(self):
        """Test default initialization."""
        logger = WinBinsLogger()

        assert logger.name == "WinBins"
        assert logger.verbose is False

    def test_init_with_options(self):
        """Test initialization with options."""
        logger = WinBinsLogger(
            name="TestLogger",
            verbose=True,
            use_colors=False
        )

        assert logger.name == "TestLogger"
        assert logger.verbose is True
        assert logger.use_colors is False

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_info(self, mock_stdout):
        """Test logging info message."""
        logger = WinBinsLogger(use_colors=False)
        logger.log("Test message", LogLevel.INFO)

        output = mock_stdout.getvalue()
        assert "[INFO]" in output
        assert "Test message" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_error(self, mock_stdout):
        """Test logging error message."""
        logger = WinBinsLogger(use_colors=False)
        logger.log("Error message", LogLevel.ERROR)

        output = mock_stdout.getvalue()
        assert "[ERROR]" in output
        assert "Error message" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_debug_verbose_off(self, mock_stdout):
        """Test debug message not shown when verbose is off."""
        logger = WinBinsLogger(verbose=False, use_colors=False)
        logger.log("Debug message", LogLevel.DEBUG)

        output = mock_stdout.getvalue()
        assert output == ""

    @patch("sys.stdout", new_callable=StringIO)
    def test_log_debug_verbose_on(self, mock_stdout):
        """Test debug message shown when verbose is on."""
        logger = WinBinsLogger(verbose=True, use_colors=False)
        logger.log("Debug message", LogLevel.DEBUG)

        output = mock_stdout.getvalue()
        assert "[DEBUG]" in output
        assert "Debug message" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_convenience_methods(self, mock_stdout):
        """Test convenience logging methods."""
        logger = WinBinsLogger(verbose=True, use_colors=False)

        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        logger.success("Success")
        logger.debug("Debug")

        output = mock_stdout.getvalue()
        assert "[INFO]" in output
        assert "[WARNING]" in output
        assert "[ERROR]" in output
        assert "[SUCCESS]" in output
        assert "[DEBUG]" in output

    def test_file_logging(self, temp_dir):
        """Test logging to file."""
        log_file = temp_dir / "test.log"
        logger = WinBinsLogger(log_file=str(log_file), use_colors=False)

        logger.info("Test log entry")

        # File handler should be set up
        assert logger._file_handler is not None


class TestLoggerFunctions:
    """Tests for logger utility functions."""

    def test_get_logger(self):
        """Test getting default logger."""
        # Reset global logger
        import winbins.logging as logging_module
        logging_module._default_logger = None

        logger = get_logger()
        assert isinstance(logger, WinBinsLogger)

    def test_get_logger_returns_same_instance(self):
        """Test get_logger returns same instance."""
        import winbins.logging as logging_module
        logging_module._default_logger = None

        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2

    def test_set_logger(self):
        """Test setting custom logger."""
        import winbins.logging as logging_module

        custom_logger = WinBinsLogger(name="Custom")
        set_logger(custom_logger)

        assert logging_module._default_logger is custom_logger
