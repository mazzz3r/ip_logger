import os
import logging
import logging.handlers
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Define log formats
VERBOSE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Get log level from environment variable
def get_log_level():
    log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return log_levels.get(log_level_str, logging.INFO)

# Configure root logger
def configure_root_logger(log_level=None):
    if log_level is None:
        log_level = get_log_level()
        
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to prevent duplication
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(SIMPLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/app.log", 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(VERBOSE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger

# Configure specific loggers
def get_logger(name, log_level=None, log_file=None):
    if log_level is None:
        log_level = get_log_level()
        
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent propagation to parent loggers to avoid duplicate logs
    logger.propagate = False
    
    # Clear existing handlers to prevent duplication when called multiple times
    if logger.handlers:
        logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(SIMPLE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (specific to this logger)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            f"logs/{log_file}", 
            maxBytes=5242880,  # 5MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(VERBOSE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Specific loggers for different components
def get_flask_logger(log_level=None):
    if log_level is None:
        log_level = get_log_level()
    return get_logger("flask", log_level, "flask.log")

def get_bot_logger(log_level=None):
    if log_level is None:
        log_level = get_log_level()
    return get_logger("bot", log_level, "bot.log")

def get_db_logger(log_level=None):
    if log_level is None:
        log_level = get_log_level()
    return get_logger("db", log_level, "db.log")

def get_request_logger(log_level=None):
    if log_level is None:
        log_level = get_log_level()
    return get_logger("request", log_level, "requests.log")

def get_error_logger(log_level=logging.ERROR):
    error_logger = get_logger("error", log_level, "error.log")
    
    # Add an additional handler for critical errors
    critical_handler = logging.handlers.RotatingFileHandler(
        "logs/critical.log", 
        maxBytes=5242880,  # 5MB
        backupCount=10
    )
    critical_handler.setLevel(logging.CRITICAL)
    critical_formatter = logging.Formatter(VERBOSE_FORMAT)
    critical_handler.setFormatter(critical_formatter)
    error_logger.addHandler(critical_handler)
    
    return error_logger

# Configure log levels based on environment
def configure_logging(environment="development"):
    if environment.lower() == "production":
        default_log_level = logging.WARNING
    elif environment.lower() == "testing":
        default_log_level = logging.DEBUG
    else:  # development
        default_log_level = logging.INFO
    
    # Override with environment variable if set
    log_level = get_log_level() or default_log_level
        
    # Configure root logger
    configure_root_logger(log_level)
    
    # Return specific loggers
    return {
        "flask": get_flask_logger(log_level),
        "bot": get_bot_logger(log_level),
        "db": get_db_logger(log_level),
        "request": get_request_logger(log_level),
        "error": get_error_logger(logging.ERROR)
    } 