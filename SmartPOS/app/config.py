import os
from dotenv import load_dotenv

load_dotenv()  # Reads a .env file in the project root, if one exists.


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "smartpos")

    LOW_STOCK_DEFAULT_THRESHOLD = 5

    # Default tax rate applied at checkout — editable per-sale on the
    # checkout screen itself (like the discount field), this is just the
    # starting value it's pre-filled with.
    DEFAULT_TAX_PERCENT = float(os.environ.get("DEFAULT_TAX_PERCENT", 0))

    # Optional — leave blank until you've created a bot via @BotFather.
    # Every Telegram notification silently no-ops if these aren't set.
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

    # Used to build the password-reset link sent via Telegram. Must be an
    # address your PHONE can actually reach -- NOT 127.0.0.1/localhost,
    # since that means "this same device" and a different device (like
    # your phone) can't resolve it back to your PC.
    #
    # Find your PC's LAN IP: Windows -> `ipconfig` (look for "IPv4
    # Address", e.g. 192.168.1.5) -- Mac/Linux -> `ifconfig` or `ip a`.
    # Then set this to that address + the port Flask runs on, e.g.:
    #   PUBLIC_BASE_URL=http://192.168.1.5:5000
    # Leave blank to fall back to whatever host the request came in on
    # (fine only if you'll always open the link from the same PC).
    PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")

    # NOTE: this file now lives at app/config.py (one level deeper than the
    # original draft's project-root config.py), so BASE_DIR goes up two
    # levels — app/config.py -> app/ -> project root — to still land on
    # the project root and keep every path below unchanged.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "products")
    AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "avatars")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB upload limit

    # Approximate USD -> Cambodian Riel exchange rate, used only for the
    # display conversion shown at checkout — never affects what's stored.
    KHR_EXCHANGE_RATE = int(os.environ.get("KHR_EXCHANGE_RATE", 4100))
