import logging
import os
from logging.handlers import RotatingFileHandler
from src import config

def setup_logging():
    """
    Configures the application's logger.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(config.LOG_FILE_PATH), exist_ok=True)

    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(config.LOG_LEVEL)

    # Prevent logging from propagating to the root logger if handlers are already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler (for printing logs to the terminal)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File Handler (for writing logs to a file)
    # RotatingFileHandler ensures log files don't grow indefinitely
    fh = RotatingFileHandler(
        config.LOG_FILE_PATH,
        maxBytes=10*1024*1024, # 10 MB
        backupCount=5
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

# Initialize the logger for the application
logger = setup_logging()
