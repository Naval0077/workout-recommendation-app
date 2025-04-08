import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workouts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing (important for form posts in Cypress)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_workouts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    SERVER_NAME = '127.0.0.1:5000'
    # DEBUG = True
