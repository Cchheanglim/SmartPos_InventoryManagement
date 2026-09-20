"""
Owns the password-reset flow, extracted from AuthService's
request_password_reset/verify_reset_token/reset_password. AuthService
still exposes those same three method names (auth_routes.py is
unchanged) and just delegates to this internally, so the reset-token
lifecycle has its own single responsibility separate from authentication.
"""
import hashlib
import secrets
from datetime import datetime, timedelta

from flask import url_for, current_app
from werkzeug.security import generate_password_hash
from app.repositories.auth.user_repository import UserRepository
from app.repositories.auth.password_reset_repository import PasswordResetRepository
from app.utils.telegram import TelegramService

RESET_TOKEN_TTL_MINUTES = 15


class PasswordResetService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.reset_repo = PasswordResetRepository()
        self.telegram = TelegramService()

    def request_password_reset(self, phone, clean_phone_fn):
        """
        Always safe to call with any input, including phone numbers that
        don't exist — the route shows the exact same message either way,
        so an anonymous visitor can never use this to discover which
        staff phone numbers are registered.

        If the account exists, a single-use reset link (valid for
        RESET_TOKEN_TTL_MINUTES) is sent to the shop's Telegram chat —
        never displayed on the page itself, since that would let anyone
        at the login screen reset an account with no proof they own it.

        clean_phone_fn: AuthService._clean_phone, passed in rather than
        duplicated here since phone-number normalization is shared with
        registration too.
        """
        clean_phone = clean_phone_fn(phone)
        user = self.user_repo.find_by_phone(clean_phone) if clean_phone else None
        if user is None or not user.is_active:
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
        self.reset_repo.set_reset_token(user.id, token_hash, expires_at)

        reset_url = self._build_reset_url(raw_token)
        self.telegram.notify_password_reset(user.name, reset_url, RESET_TOKEN_TTL_MINUTES)

    @staticmethod
    def _build_reset_url(raw_token):
        """
        Prefers Config.PUBLIC_BASE_URL (a LAN IP or real domain) so the
        link works from a different device, like the phone that reads
        the Telegram message. Falls back to url_for's own host detection
        only if that setting is blank.
        """
        base_url = current_app.config.get("PUBLIC_BASE_URL", "")
        if base_url:
            return f"{base_url}{url_for('auth.reset_password', token=raw_token)}"
        return url_for("auth.reset_password", token=raw_token, _external=True)

    def verify_reset_token(self, raw_token):
        """Returns the User if raw_token is valid and unexpired, else None."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        return self.reset_repo.find_by_valid_reset_token_hash(token_hash)

    def reset_password(self, raw_token, new_password):
        """Completes a reset. Raises ValueError on an invalid/expired
        token or a too-short password — the token is single-use, so it's
        cleared the moment it succeeds."""
        user = self.verify_reset_token(raw_token)
        if user is None:
            raise ValueError("This reset link is invalid or has expired.")
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters.")
        self.user_repo.update_password_hash(user.id, generate_password_hash(new_password))
        self.reset_repo.clear_reset_token(user.id)
