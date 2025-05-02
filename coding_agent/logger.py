import os
import logging
from datetime import datetime
from coding_agent.config import LOG_DIR


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Configure and return a logger instance."""
    os.makedirs(LOG_DIR, exist_ok=True)

    if log_file is None:
        log_file = os.path.join(LOG_DIR,
                                f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    return logger