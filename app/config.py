import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workouts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing (important for form posts in Cypress)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_workouts.db'
    DEBUG = True
