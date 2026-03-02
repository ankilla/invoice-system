#!/usr/bin/env python3
"""
Invoice Generation System - Launcher
Starts the web server and opens the browser automatically.
"""
import os, sys, time, subprocess, webbrowser, threading

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def open_browser():
    time.sleep(2)
    webbrowser.open(f'http://localhost:{PORT}')

def main():
    # Init DB
    sys.path.insert(0, BASE_DIR)
    from database import init_db
    init_db()

    print("=" * 55)
    print("  📄  INVOICE GENERATION SYSTEM")
    print("=" * 55)
    print(f"  ✅  Server starting on http://localhost:{PORT}")
    print(f"  🌐  Opening browser automatically...")
    print(f"  ⏹   Press Ctrl+C to stop")
    print("=" * 55)

    threading.Thread(target=open_browser, daemon=True).start()

    from app import app
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    main()
