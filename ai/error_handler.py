"""Error handling and logging utilities."""

import sys
import traceback
import logging
from pathlib import Path
from typing import Optional, Any, Callable
from functools import wraps
from datetime import datetime

from config.settings import settings


class LeCodeError(Exception):
    """Base exception for le-code errors."""

    pass


class APIError(LeCodeError):
    """API-related errors."""

    pass


class FileOperationError(LeCodeError):
    """File operation errors."""

    pass


class CommandExecutionError(LeCodeError):
    """Command execution errors."""

    pass


class ConfigurationError(LeCodeError):
    """Configuration errors."""

    pass


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_dir = settings.SESSIONS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"le-code-{datetime.now().strftime('%Y%m%d')}.log"

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr)
        ]
    )

    logger = logging.getLogger('le-code')
    logger.info(f"Logging initialized. Log file: {log_file}")


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for handling errors in functions.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except LeCodeError as e:
            logger = logging.getLogger('le-code')
            logger.error(f"{type(e).__name__}: {e}")
            print(f"[Error: {e}]")
            return None
        except Exception as e:
            logger = logging.getLogger('le-code')
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            logger.debug(traceback.format_exc())
            print(f"[Unexpected error: {e}]")
            return None

    return wrapper


def retry_on_error(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions on error.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for backoff delay
        exceptions: Exceptions to catch and retry on

    Returns:
        Decorator function
    """
    import time

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('le-code')

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise

                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)

            return None

        return wrapper

    return decorator


class ErrorHandler:
    """Centralized error handler for the application."""

    def __init__(self):
        """Initialize the error handler."""
        self.logger = logging.getLogger('le-code')
        self.error_counts: dict = {}

    def handle_api_error(self, error: Exception) -> str:
        """
        Handle API-related errors.

        Args:
            error: Exception that occurred

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Handle specific error types
        if "RateLimitError" in str(type(error)):
            return "API rate limit exceeded. Please wait a moment and try again."
        elif "APIConnectionError" in str(type(error)):
            return "Could not connect to API. Please check your internet connection."
        elif "APIError" in str(type(error)):
            return f"API error: {str(error)}"
        else:
            return f"Unexpected API error: {str(error)}"

    def handle_file_error(self, error: Exception) -> str:
        """
        Handle file operation errors.

        Args:
            error: Exception that occurred

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        if "FileNotFoundError" in error_type:
            return "File not found. Please check the file path."
        elif "PermissionError" in error_type:
            return "Permission denied. Please check file permissions."
        elif "UnicodeDecodeError" in error_type:
            return "Could not decode file. It may be a binary file."
        else:
            return f"File operation error: {str(error)}"

    def handle_command_error(self, error: Exception) -> str:
        """
        Handle command execution errors.

        Args:
            error: Exception that occurred

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        if "TimeoutExpired" in error_type:
            return f"Command timed out after {settings.SHELL_TIMEOUT} seconds."
        elif "KeyboardInterrupt" in error_type:
            return "Command interrupted by user."
        elif "subprocess.SubprocessError" in str(type(error)):
            return f"Command execution error: {str(error)}"
        else:
            return f"Command error: {str(error)}"

    def handle_config_error(self, error: Exception) -> str:
        """
        Handle configuration errors.

        Args:
            error: Exception that occurred

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        return f"Configuration error: {str(error)}"

    def log_error(self, error: Exception, context: Optional[dict] = None) -> None:
        """
        Log an error with context.

        Args:
            error: Exception that occurred
            context: Optional context dictionary
        """
        self.logger.error(
            f"{type(error).__name__}: {str(error)}",
            extra={"context": context or {}}
        )

    def get_error_summary(self) -> dict:
        """
        Get a summary of errors encountered.

        Returns:
            Dictionary of error types and counts
        """
        return self.error_counts.copy()

    def reset_error_counts(self) -> None:
        """Reset error count statistics."""
        self.error_counts.clear()


# Create default error handler instance
default_error_handler = ErrorHandler()
