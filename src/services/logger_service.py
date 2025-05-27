import logging
import sys

# ANSI escape codes for colors
LOG_COLORS = {
    "DEBUG": "\033[34m",  # Blue
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[1;31m",  # Bright Red
}
RESET_COLOR = "\033[0m"


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors based on log level.
    """

    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, "")
        reset = RESET_COLOR

        formatted_message = super().format(record)
        return f"{log_color}{formatted_message}{reset}"


def get_logger(name: str = "fastapi_app") -> logging.Logger:
    """
    Returns a configured logger instance.
    """

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)  # Default level

    # Formatter
    log_format = "%(levelname)s — %(message)s"
    formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # StreamHandler (console output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


logger = get_logger()
