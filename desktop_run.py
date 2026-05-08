"""
desktop_run.py — Entry point for Ali Mobiles Billing Software
Works both as normal Python script and as PyInstaller EXE.
"""
import os
import sys
import threading
import webbrowser
import time

# ── Working directory fix (must happen BEFORE importing app) ────────────
if getattr(sys, 'frozen', False):
    # Running as EXE: work dir = folder containing the .exe
    WORK_DIR = os.path.dirname(sys.executable)
    BASE_DIR  = sys._MEIPASS
else:
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR  = WORK_DIR

os.chdir(WORK_DIR)
sys.path.insert(0, BASE_DIR)

# ── Now import Flask app ────────────────────────────────────────────────
from app import app

PORT = 5055
URL  = f"http://127.0.0.1:{PORT}"


def run_flask():
    """Run Flask server (production mode — no debug, no reloader)."""
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    # Start Flask in a background daemon thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait briefly for Flask to initialize
    time.sleep(1.8)

    # Try to open in native desktop window via pywebview
    try:
        import webview
        webview.create_window(
            title      = "Ali Mobiles — Billing Software v2.0",
            url        = URL,
            width      = 1280,
            height     = 800,
            resizable  = True,
            min_size   = (900, 600),
        )
        webview.start()
        # When webview window closes, app exits automatically (daemon thread)

    except Exception:
        # Fallback: open in system default browser
        webbrowser.open(URL)
        print("=" * 55)
        print(" Ali Mobiles Billing Software")
        print(f" Running at: {URL}")
        print(" Browser mein khul gaya hai.")
        print(" Band karne ke liye yeh window band karo.")
        print("=" * 55)

        # Keep main thread alive until user closes console
        try:
            while flask_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nServer band ho gaya. Khuda Hafiz!")
            sys.exit(0)
