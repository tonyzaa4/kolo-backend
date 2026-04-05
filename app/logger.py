import logging
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure a dedicated logger for catalog access logs."""
    logger = logging.getLogger("api_access")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    log_path = Path("api_access.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
