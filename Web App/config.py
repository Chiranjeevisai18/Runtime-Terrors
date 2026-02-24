"""
Configuration settings for Gruha Alankara Web Application.
Contains database, upload, and security configurations.
"""

import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Main configuration class for Flask application."""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gruha-alankara-secret-key-change-in-production')
    
    # SQLite database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'gruha_alankara.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout
    
    # AI Model configuration
    AI_MODEL_CACHE_DIR = os.path.join(BASE_DIR, 'model_cache')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_UPLOAD = "10 per minute"

    # Gemini AI API key for Design Assistant
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAoAMrlVClmXE6ye_1kr6X8Ey5jix9ckQY')

    # Tavily Search API key for product recommendations
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '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')
