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


def _print(msg: str):
    """Print with flush so it shows immediately in PowerShell."""
    print(msg, flush=True)


# Make sure temp dirs exist next to the exe / source
base = _base_path()
os.makedirs(os.path.join(base, "uploads"), exist_ok=True)
os.makedirs(os.path.join(base, "results"), exist_ok=True)
os.chdir(base)

_print("Starting BG Cleaner...")
_print("Loading AI model (this takes ~1 minute on first run)...")

from app import create_app

if __name__ == "__main__":
    application = create_app()

    # Cloud platforms (Railway, Render, Heroku) set PORT env var
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    url = f"http://localhost:{port}"

    _print("")
    _print("=" * 50)
    _print(f"  BG Cleaner is ready!")
    _print(f"  Opening browser at: {url}")
    _print("=" * 50)
    _print("")
    _print("  If browser does not open, visit:")
    _print(f"  {url}")
    _print("")
    _print("  Press Ctrl+C to quit.")
    _print("")

    # Only open browser when running locally (not on Railway/Render)
    if not os.environ.get("PORT"):
        def _open_browser():
            time.sleep(1)
            try:
                webbrowser.open(url)
            except Exception:
                try:
                    if sys.platform == "win32":
                        os.startfile(url)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", url])
                    else:
                        subprocess.Popen(["xdg-open", url])
                except Exception:
                    _print(f"\n  Please open manually: {url}\n")

        threading.Thread(target=_open_browser, daemon=True).start()

    application.run(debug=False, host=host, port=port)
