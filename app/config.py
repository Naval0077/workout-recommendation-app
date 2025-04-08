import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workouts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5000'  # Critical for URL generation
    APPLICATION_ROOT = '/'  # Explicit root path
    PREFERRED_URL_SCHEME = 'http'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///test_workouts.db')
    # DEBUG = True
