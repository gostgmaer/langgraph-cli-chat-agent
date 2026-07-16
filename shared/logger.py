# ============================================================
# shared/logger.py — Application Logger
# ============================================================
# TODO: Configure logging with Rich, JSON, or plain handler
# TODO: Set log level from LOG_LEVEL env variable
# TODO: Optionally write logs to LOG_FILE
# TODO: Expose a `get_logger(name)` function
# ============================================================


"""
Centralized application logger.

Every module should import the logger from here.

Example:
    from shared.logger import logger

    logger.debug("Application started")
"""

from logging import INFO, getLogger
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

from config.settings import settings


def create_logger():
    """Create and configure the application logger."""

    logger = getLogger(settings.app_name)

    if logger.handlers:
        return logger

    logger.setLevel(settings.log_level)

    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
    )

    file_handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    console_handler.setLevel(INFO)
    file_handler.setLevel(INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


logger = create_logger()