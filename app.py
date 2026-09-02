"""Entry point — run with: python app.py or BG Cleaner.exe"""

import sys
import os
import webbrowser
import threading
import time
import subprocess


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
    url = f"http://localhost:{port}"

    # Only open browser when running locally (not on Railway/Render)
    if not os.environ.get("PORT"):
        def _open_browser():
            # Wait for server to be ready
            time.sleep(2)
            try:
                # Try webbrowser module first
                webbrowser.open(url)
            except Exception:
                # Fallback: use system command
                try:
                    if sys.platform == "win32":
                        subprocess.Popen(["cmd", "/c", "start", url], shell=False)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", url])
                    else:
                        subprocess.Popen(["xdg-open", url])
                except Exception:
                    pass

        threading.Thread(target=_open_browser, daemon=True).start()

    print(f"\n  {'='*50}")
    print(f"  BG Cleaner is running!")
    print(f"  Open this URL in your browser: {url}")
    print(f"  {'='*50}\n")
    print(f"  Press Ctrl+C to quit.\n")

    application.run(debug=False, host=host, port=port)
