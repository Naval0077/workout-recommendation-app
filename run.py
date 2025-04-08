from app import create_app
import os

from app.config import TestingConfig

env = os.getenv("FLASK_ENV")

if env == "testing":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app = create_app(TestingConfig)
else:
    app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


