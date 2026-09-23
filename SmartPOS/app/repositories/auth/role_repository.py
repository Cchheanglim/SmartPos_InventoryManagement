from app.extensions import get_db
from app.models.auth.role import Role
from app.models.auth.permission import Permission


class RoleRepository:
    """Only this class writes MySQL queries for the roles table."""

    def find_by_id(self, role_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
            return Role.from_row(cur.fetchone())

    def find_by_name(self, name):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM roles WHERE name = %s", (name,))
            return Role.from_row(cur.fetchone())

    def list_all(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM roles ORDER BY name")
            return [Role.from_row(row) for row in cur.fetchall()]

    def list_with_user_counts(self):
        """Returns all roles along with the number of users currently assigned to each."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT r.id, r.name, COUNT(u.id) AS user_count
                   FROM roles r
                   LEFT JOIN users u ON r.id = u.role_id
                   GROUP BY r.id, r.name
                   ORDER BY (r.name = 'admin') DESC, r.name ASC"""
            )
            return [Role.from_row(row) for row in cur.fetchall()]

    def count_users_with_role(self, role_id):
        """Returns how many users are assigned to this role_id."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM users WHERE role_id = %s", (role_id,))
            row = cur.fetchone()
            return row["total"] if row else 0

    def create(self, name):
        """Inserts a new role by name using parameterized query."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("INSERT INTO roles (name) VALUES (%s)", (name,))
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def update(self, role_id, name):
        """Renames an existing role."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE roles SET name = %s WHERE id = %s", (name, role_id))
        db.commit()

    def delete(self, role_id):
        """Deletes a role from MySQL. Relies on ON DELETE CASCADE for role_permissions."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("DELETE FROM roles WHERE id = %s", (role_id,))
        db.commit()

    def roles_with_permission(self, permission_name):
        """Returns all roles that currently hold the specified permission name."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT r.* FROM roles r
                   JOIN role_permissions rp ON r.id = rp.role_id
                   JOIN permissions p ON rp.permission_id = p.id
                   WHERE p.name = %s""",
                (permission_name,),
            )
            return [Role.from_row(row) for row in cur.fetchall()]


class PermissionRepository:
    """Only this class writes MySQL queries for the permissions and role_permissions tables."""

    def list_all(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM permissions ORDER BY name")
            return [Permission.from_row(row) for row in cur.fetchall()]

    def find_by_id(self, permission_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM permissions WHERE id = %s", (permission_id,))
            return Permission.from_row(cur.fetchone())

    def find_by_name(self, name):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM permissions WHERE name = %s", (name,))
            return Permission.from_row(cur.fetchone())

    def create(self, name, description=None):
        """Creates a new permission. Checks if description column exists in permissions table."""
        db = get_db()
        with db.cursor() as cur:
            try:
                cur.execute("INSERT INTO permissions (name, description) VALUES (%s, %s)", (name, description))
            except Exception:
                # If description column does not exist in schema, fallback to name only
                cur.execute("INSERT INTO permissions (name) VALUES (%s)", (name,))
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def update(self, permission_id, name, description=None):
        """Renames or updates an existing permission."""
        db = get_db()
        with db.cursor() as cur:
            try:
                cur.execute("UPDATE permissions SET name = %s, description = %s WHERE id = %s", (name, description, permission_id))
            except Exception:
                cur.execute("UPDATE permissions SET name = %s WHERE id = %s", (name, permission_id))
        db.commit()

    def delete(self, permission_id):
        """Deletes a permission. Foreign keys cascade delete from role_permissions and user_permissions."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("DELETE FROM permissions WHERE id = %s", (permission_id,))
        db.commit()

    def list_for_role(self, role_id):
        """Returns the set of permission names a role holds, via role_permissions."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT p.name FROM permissions p
                   JOIN role_permissions rp ON p.id = rp.permission_id
                   WHERE rp.role_id = %s""",
                (role_id,),
            )
            return {row["name"] for row in cur.fetchall()}

    def list_permission_ids_for_role(self, role_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT permission_id FROM role_permissions WHERE role_id = %s", (role_id,))
            return {row["permission_id"] for row in cur.fetchall()}

    def set_role_permissions(self, role_id, permission_ids):
        """Replaces a role's entire permission set with exactly the given
        list — this is what lets an Admin reconfigure permissions from the
        UI instead of needing to edit code or seed data."""
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("DELETE FROM role_permissions WHERE role_id = %s", (role_id,))
            for pid in permission_ids:
                cur.execute(
                    "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
                    (role_id, pid),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cur.close()

    def list_extra_permission_names_for_user(self, user_id):
        """The individual permission grants an Admin has given this one
        person, on top of their role — used to compute their real total
        permission set alongside the role's own permissions."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT p.name FROM permissions p
                   JOIN user_permissions up ON p.id = up.permission_id
                   WHERE up.user_id = %s""",
                (user_id,),
            )
            return {row["name"] for row in cur.fetchall()}

    def list_extra_permission_ids_for_user(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT permission_id FROM user_permissions WHERE user_id = %s", (user_id,))
            return {row["permission_id"] for row in cur.fetchall()}

    def set_user_permissions(self, user_id, permission_ids, granted_by):
        """Replaces this user's entire set of individually-granted extra
        permissions. Never touches role_permissions — this is purely
        additive on top of whatever their role already gives them."""
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("DELETE FROM user_permissions WHERE user_id = %s", (user_id,))
            for pid in permission_ids:
                cur.execute(
                    "INSERT INTO user_permissions (user_id, permission_id, granted_by) VALUES (%s, %s, %s)",
                    (user_id, pid, granted_by),
                )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            cur.close()

    def ensure_permission_exists(self, name, description=None, default_role_name="admin"):
        """Ensures a permission exists in the database and is seeded for default_role_name."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT id FROM permissions WHERE name = %s", (name,))
            perm_row = cur.fetchone()
            if not perm_row:
                try:
                    cur.execute("INSERT INTO permissions (name, description) VALUES (%s, %s)", (name, description))
                except Exception:
                    cur.execute("INSERT INTO permissions (name) VALUES (%s)", (name,))
                perm_id = cur.lastrowid
            else:
                perm_id = perm_row["id"]

            if default_role_name:
                cur.execute("SELECT id FROM roles WHERE name = %s", (default_role_name,))
                role_row = cur.fetchone()
                if role_row:
                    cur.execute(
                        "SELECT COUNT(*) AS total FROM role_permissions WHERE role_id = %s AND permission_id = %s",
                        (role_row["id"], perm_id)
                    )
                    exists = cur.fetchone()["total"] > 0
                    if not exists:
                        cur.execute(
                            "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
                            (role_row["id"], perm_id)
                        )
        db.commit()
        return perm_id

