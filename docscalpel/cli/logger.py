"""
Logging configuration for CLI.

Provides structured logging setup with appropriate levels and formatting.
Logs to stderr to keep stdout clean for data output.
"""

import logging
import sys


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for CLI application.

    Args:
        verbose: If True, set log level to DEBUG; otherwise INFO

    Example:
        >>> setup_logging(verbose=True)
        >>> logger = logging.getLogger(__name__)
        >>> logger.debug("Detailed debug information")
    """
    # Determine log level
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Create stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(log_level)
    stderr_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(stderr_handler)

    # Set library logger levels
    lib_logger = logging.getLogger('src.lib')
    lib_logger.setLevel(log_level)

    cli_logger = logging.getLogger('src.cli')
    cli_logger.setLevel(log_level)

    # Suppress overly verbose third-party loggers
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    if verbose:
        root_logger.debug("Verbose logging enabled")
