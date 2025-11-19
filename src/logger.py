import logging
import os

#create logs directory if needed
os.makedirs('logs',exist_ok=True)

LOG_FILE = "logs/project.log"

def setup_logger(name='ProjectLogger'):
    """Return a logger with console + file handlers configured globally."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG) # capture everything: DEBUG, INFO, WARNING, ERROR

    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File Handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Log Format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    return logger


logger = setup_logger()

