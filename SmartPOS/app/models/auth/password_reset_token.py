"""
No separate PasswordResetToken class exists because a reset token isn't
its own entity — it's three columns directly on the users row
(`reset_token_hash`, `reset_token_expires_at`; see sql/schema.sql,
CREATE TABLE users), since a user only ever has at most one active reset
token at a time. UserRepository already has the full lifecycle for this:
set_reset_token, find_by_valid_reset_token_hash, clear_reset_token
(app/repositories/auth/user_repository.py), called from
AuthService.request_password_reset/reset_password.

This file intentionally has no class — a PasswordResetToken object with
no table of its own to back it would just wrap those same three columns
for no behavior gain.
"""
