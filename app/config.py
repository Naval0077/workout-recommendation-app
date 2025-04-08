import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workouts.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_workouts.db'
    SECRET_KEY = 'test-secret-key'
    SERVER_NAME = 'localhost:5000'
    SESSION_TYPE = 'filesystem'
    # DEBUG = True
