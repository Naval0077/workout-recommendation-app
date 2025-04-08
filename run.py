from app import create_app
import os

from app.config import TestingConfig

env = os.getenv("FLASK_ENV")

if env == "testing":
    app = create_app(TestingConfig)
else:
    app = create_app()

if __name__ == "__main__":
    app.run()


