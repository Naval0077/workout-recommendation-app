from app import create_app
import os
app = create_app()
print("== Flask is starting with config:", os.getenv("FLASK_CONFIG"))

if __name__ == "__main__":
    app.run( threaded=True)


