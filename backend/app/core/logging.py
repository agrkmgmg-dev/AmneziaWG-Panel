"""
Application logging configuration.

Production-ready logging setup.

Features:
- Console logging
- Rotating file logging
- Configurable log level
- Prevent duplicate handlers
"""

import logging
import logging.handlers
import sys
from pathlib import Path

from backend.app.core.config import settings


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def setup_logging() -> None:
    """
    Configure application logging.

    Should be called once during application startup.
    """

    log_level = getattr(
        logging,
        settings.LOG_LEVEL.upper(),
        logging.INFO
    )

    formatter = logging.Formatter(
        LOG_FORMAT
    )

    root_logger = logging.getLogger()

    root_logger.setLevel(
        log_level
    )

    # Prevent duplicate handlers
    if root_logger.handlers:
        return


    # -----------------------------
    # Console Handler
    # -----------------------------

    console_handler = logging.StreamHandler(
        sys.stdout
    )

    console_handler.setLevel(
        log_level
    )

    console_handler.setFormatter(
        formatter
    )

    root_logger.addHandler(
        console_handler
    )


    # -----------------------------
    # File Handler
    # -----------------------------

    log_file = Path(
        settings.LOG_FILE
    )

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setLevel(
        log_level
    )

    file_handler.setFormatter(
        formatter
    )

    root_logger.addHandler(
        file_handler
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get application logger instance.
    """

    return logging.getLogger(name)