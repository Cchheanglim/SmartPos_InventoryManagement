"""Entry point. Run with: python main.py"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # host="0.0.0.0" makes the server listen on your LAN, not just this
    # machine — required so your phone can reach it (e.g. for the
    # password-reset link, or barcode scanning from a phone camera).
    # If it doesn't work from your phone, check that Windows Firewall
    # isn't blocking incoming connections on this port.
    app.run(debug=True, host="0.0.0.0")
