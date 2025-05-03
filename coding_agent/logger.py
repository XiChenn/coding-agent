import os
import logging
from datetime import datetime
from coding_agent.config import LOG_DIR

log_dir = LOG_DIR or os.path.join(os.getcwd(), "logs")


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Configure and return a logger instance."""
    os.makedirs(log_dir, exist_ok=True)

    if log_file is None:
        log_file = os.path.join(log_dir,
                                f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers.
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

    return logger