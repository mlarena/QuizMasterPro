import logging
from logging.handlers import RotatingFileHandler
from app.config import Config
import os
from datetime import date

def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    os.makedirs(Config.LOG_FOLDER, exist_ok=True)
    
    today = date.today().isoformat()
    log_file = os.path.join(Config.LOG_FOLDER, f'app_{today}.log')
    error_log_file = os.path.join(Config.LOG_FOLDER, f'errors_{today}.log')
    
    # Formatter for logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Main logger for all events
    logger = logging.getLogger('quizmaster')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Clear any existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # File handler for all events
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error handler (ERROR and above)
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Console output for development
    if os.environ.get('FLASK_ENV') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger