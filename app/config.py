import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-quizmaster-pro'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Path(__file__).parent.parent, 'quizmaster.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging settings
    LOG_FOLDER = os.path.join(Path(__file__).parent.parent, 'logs')
    LOG_FILE = os.path.join(LOG_FOLDER, 'quizmaster.log')
    ERROR_LOG_FILE = os.path.join(LOG_FOLDER, 'errors.log')
    LOG_LEVEL = 'INFO'
    
    # Material UI color scheme
    THEME_COLORS = {
        'primary': '#1976d2',
        'secondary': '#9c27b0',
        'error': '#d32f2f',
        'warning': '#ed6c02',
        'info': '#0288d1',
        'success': '#2e7d32',
        'background': '#f5f5f5',
        'text_primary': 'rgba(0, 0, 0, 0.87)',
        'text_secondary': 'rgba(0, 0, 0, 0.6)'
    }