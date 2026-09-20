from app.extensions import get_db
from app.models.auth.role import Role
from app.models.auth.permission import Permission


class RoleRepository:
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


class PermissionRepository:
    def list_all(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM permissions ORDER BY name")
            return [Permission.from_row(row) for row in cur.fetchall()]

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
