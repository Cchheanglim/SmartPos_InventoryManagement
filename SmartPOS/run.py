#!/usr/bin/env python3
"""
SmartPOS - Advanced OOP with Python
Flask Application Runner

Course: Advanced OOP with Python
Lecturer: SEK SOCHEAT

Conforms to standard project entry point:
    python run.py
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    # host="0.0.0.0" enables LAN access for mobile/tablet barcode scanning & POS terminals
    app.run(host="0.0.0.0", port=port, debug=debug)
