from app import create_app
import os
app = create_app()
print("== Flask is starting with config:", os.getenv("FLASK_CONFIG"))
if os.environ.get('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestingConfig')

if __name__ == "__main__":
    app.run( threaded=True)


