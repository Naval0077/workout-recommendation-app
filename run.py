from app import create_app
import os
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT; default to 10000 if missing
    app.run(host="0.0.0.0", port=port, threaded=True)

