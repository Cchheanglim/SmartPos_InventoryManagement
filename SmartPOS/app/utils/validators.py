"""
Small, reusable, dependency-free validation helpers. Each existing route
already validates its own inputs inline (see the try/except ValueError
pattern throughout app/routes/) — these exist for new code that wants a
shared, tested implementation instead of re-writing the same regex or
range check in a fourth place.
"""
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^[\d\s\-\+\(\)]{7,20}$")


def is_valid_email(value: str) -> bool:
    return bool(value) and bool(_EMAIL_RE.match(value.strip()))


def is_valid_phone(value: str) -> bool:
    return bool(value) and bool(_PHONE_RE.match(value.strip()))


def is_positive_number(value, allow_zero: bool = True) -> bool:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return False
    return n >= 0 if allow_zero else n > 0


def is_non_empty(value) -> bool:
    return bool(value) and bool(str(value).strip())


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))
