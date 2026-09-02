"""Entry point — run with: python app.py or BG Cleaner.exe"""

import sys
import os
import webbrowser
import threading
import time


def _base_path() -> str:
    """Return the directory containing the exe (or app.py when running from source)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# Make sure temp dirs exist next to the exe / source
base = _base_path()
os.makedirs(os.path.join(base, "uploads"), exist_ok=True)
os.makedirs(os.path.join(base, "results"), exist_ok=True)
os.chdir(base)

from app import create_app

if __name__ == "__main__":
    application = create_app()

    # Cloud platforms (Railway, Render, Heroku) set PORT env var
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"

    # Only open browser when running locally
    if not os.environ.get("PORT"):
        def _open_browser():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")
        threading.Thread(target=_open_browser, daemon=True).start()

    print(f"\n  BG Cleaner is running at  http://{host}:{port}\n  Press Ctrl+C to quit.\n")
    application.run(debug=False, host=host, port=port)
