from app.extensions import get_db
from app.models.auth.user import User


class UserRepository:
    """Only this class writes MySQL queries for the users table."""

    def find_by_id(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT u.*, r.name AS role_name
                   FROM users u JOIN roles r ON u.role_id = r.id
                   WHERE u.id = %s""",
                (user_id,),
            )
            return User.from_row(cur.fetchone())

    def find_by_email(self, email):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT u.*, r.name AS role_name
                   FROM users u JOIN roles r ON u.role_id = r.id
                   WHERE u.email = %s""",
                (email,),
            )
            return User.from_row(cur.fetchone())

    def find_by_phone(self, phone):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT u.*, r.name AS role_name
                   FROM users u JOIN roles r ON u.role_id = r.id
                   WHERE u.phone = %s""",
                (phone,),
            )
            return User.from_row(cur.fetchone())

    def list_all(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT u.*, r.name AS role_name
                   FROM users u JOIN roles r ON u.role_id = r.id
                   ORDER BY u.name"""
            )
            return [User.from_row(row) for row in cur.fetchall()]

    def create(self, name, email, password_hash, role_id, phone=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO users (name, email, phone, password_hash, role_id)
                   VALUES (%s, %s, %s, %s, %s)""",
                (name, email, phone, password_hash, role_id),
            )
        db.commit()
        return cur.lastrowid

    def update_email(self, user_id, email):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
        db.commit()

    def update_name(self, user_id, name):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET name = %s WHERE id = %s", (name, user_id))
        db.commit()

    def update_phone(self, user_id, phone):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET phone = %s WHERE id = %s", (phone, user_id))
        db.commit()

    def set_active(self, user_id, is_active):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id))
        db.commit()

    def update_profile_picture(self, user_id, filename):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET profile_picture = %s WHERE id = %s", (filename, user_id))
        db.commit()

    def update_password_hash(self, user_id, password_hash):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
        db.commit()

    # Reset-token methods (set_reset_token, find_by_valid_reset_token_hash,
    # clear_reset_token) moved to
    # app/repositories/auth/password_reset_repository.py (PasswordResetRepository).

    def update_role(self, user_id, role_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE users SET role_id = %s WHERE id = %s", (role_id, user_id))
        db.commit()

    def set_shift(self, user_id, shift_name, shift_start, shift_end):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE users SET shift_name = %s, shift_start = %s, shift_end = %s WHERE id = %s",
                (shift_name, shift_start, shift_end, user_id),
            )
        db.commit()
