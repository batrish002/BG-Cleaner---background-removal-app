"""Entry point — run with: python app.py or BG Cleaner.exe"""

import sys
import os
import webbrowser
import threading
import time
import subprocess
import socket


def _base_path() -> str:
    """Return the directory containing the exe (or app.py when running from source)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _print(msg: str):
    """Print with flush so it shows immediately in PowerShell."""
    print(msg, flush=True)


def _wait_for_server(host: str, port: int, timeout: int = 120) -> bool:
    """Wait until the server is accepting connections."""
    url = f"http://{host}:{port}"
    _print(f"  Waiting for server at {url}...")
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.create_connection((host, port), timeout=2)
            sock.close()
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(1)
    return False


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

    # Only open browser when running locally (not on Railway/Render)
    if not os.environ.get("PORT"):
        def _open_browser():
            # Wait for server to actually be ready
            if _wait_for_server("127.0.0.1", port, timeout=120):
                _print(f"  Server ready! Opening browser...")
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
            else:
                _print(f"\n  Server took too long to start.")
                _print(f"  Please open manually: {url}\n")

        threading.Thread(target=_open_browser, daemon=True).start()

    _print("")
    _print("=" * 50)
    _print(f"  BG Cleaner is starting...")
    _print(f"  URL: {url}")
    _print("=" * 50)
    _print("")
    _print("  Press Ctrl+C to quit.")
    _print("")

    application.run(debug=False, host=host, port=port)
