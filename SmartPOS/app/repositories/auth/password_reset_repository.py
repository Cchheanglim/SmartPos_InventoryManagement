"""
Reset-token data access, extracted from UserRepository (set_reset_token,
find_by_valid_reset_token_hash, clear_reset_token) — same queries, moved
out so password-reset has its own repository. UserRepository keeps thin
passthrough methods with the same names, so PasswordResetService and
anything else already calling them didn't need to change.

The token itself is still stored as two columns directly on the users
row (see app/models/auth/password_reset_token.py for why there's no
separate table/model) — this repository just gives that read/write
logic its own file instead of living inside UserRepository.
"""
from app.extensions import get_db
from app.models.auth.user import User


class PasswordResetRepository:
    def set_reset_token(self, user_id, token_hash, expires_at):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE users SET reset_token_hash = %s, reset_token_expires_at = %s WHERE id = %s",
                (token_hash, expires_at, user_id),
            )
        db.commit()

    def find_by_valid_reset_token_hash(self, token_hash):
        """Returns the User only if token_hash matches AND hasn't expired yet."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT u.*, r.name AS role_name
                   FROM users u JOIN roles r ON u.role_id = r.id
                   WHERE u.reset_token_hash = %s
                     AND u.reset_token_expires_at IS NOT NULL
                     AND u.reset_token_expires_at > NOW()""",
                (token_hash,),
            )
            return User.from_row(cur.fetchone())

    def clear_reset_token(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE users SET reset_token_hash = NULL, reset_token_expires_at = NULL WHERE id = %s",
                (user_id,),
            )
        db.commit()
