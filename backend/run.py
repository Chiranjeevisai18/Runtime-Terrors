from app import create_app
import os

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    # In development, use 5000
    app.run(host="0.0.0.0", port=5000, debug=False) # Debug False to avoid reloading issues with large models
