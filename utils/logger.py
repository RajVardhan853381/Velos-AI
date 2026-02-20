"""
Centralized logging configuration for Velos AI
Replaces scattered print() statements with structured logging
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOGS_DIR / f"velos_{datetime.now().strftime('%Y%m%d')}.log"

# Custom formatter with colors for console
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[0;36m',     # Cyan
        'INFO': '\033[0;32m',      # Green
        'WARNING': '\033[1;33m',   # Yellow
        'ERROR': '\033[0;31m',     # Red
        'CRITICAL': '\033[1;35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(name: str = "velos", level: str = "INFO") -> logging.Logger:
    """
    Setup centralized logging for the application
    
    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(
        '%(levelname)s | %(name)s | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler (detailed, no colors)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Create module-level loggers for easy import
logger = setup_logging("velos")
agent_logger = setup_logging("velos.agents")
api_logger = setup_logging("velos.api")
db_logger = setup_logging("velos.database")
utils_logger = setup_logging("velos.utils")


# Convenience functions for common logging patterns
def log_api_request(endpoint: str, method: str = "GET", **kwargs):
    """Log API request"""
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    api_logger.info(f"API {method} {endpoint} {('| ' + extra_info) if extra_info else ''}")


def log_agent_action(agent_name: str, action: str, **kwargs):
    """Log agent action"""
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    agent_logger.info(f"{agent_name}: {action} {('| ' + extra_info) if extra_info else ''}")


def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    logger.error(f"{context}: {type(error).__name__}: {str(error)}", exc_info=True)


# Export all
__all__ = [
    'logger',
    'agent_logger',
    'api_logger',
    'db_logger',
    'utils_logger',
    'setup_logging',
    'log_api_request',
    'log_agent_action',
    'log_error',
]
