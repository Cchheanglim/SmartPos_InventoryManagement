"""
Thin wrappers around Werkzeug's password hashing, so callers depend on
this module rather than importing werkzeug.security directly — if the
hashing scheme ever needs to change app-wide, it changes in one place.

Not currently wired into auth_service.py (which calls
werkzeug.security.generate_password_hash/check_password_hash directly,
and is already tested that way) — these do the exact same thing, and are
here for any new code that wants a single, obvious import.
"""
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, plain_password)


def is_strong_enough(plain_password: str, min_length: int = 6) -> bool:
    """Matches the minimum length AuthService already enforces on
    registration and password changes/resets."""
    return bool(plain_password) and len(plain_password) >= min_length
