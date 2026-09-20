from app.extensions import get_db
from app.models.staff.task import Task


class TaskRepository:
    """Only this class writes MySQL queries for the tasks table."""

    def create(self, title, description, assigned_to, assigned_by):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO tasks (title, description, assigned_to, assigned_by)
                   VALUES (%s, %s, %s, %s)""",
                (title, description, assigned_to, assigned_by),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def find_by_id(self, task_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT t.*, u1.name AS assigned_to_name, u2.name AS assigned_by_name
                   FROM tasks t
                   JOIN users u1 ON t.assigned_to = u1.id
                   JOIN users u2 ON t.assigned_by = u2.id
                   WHERE t.id = %s""",
                (task_id,),
            )
            return Task.from_row(cur.fetchone())

    def list_all(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT t.*, u1.name AS assigned_to_name, u2.name AS assigned_by_name
                   FROM tasks t
                   JOIN users u1 ON t.assigned_to = u1.id
                   JOIN users u2 ON t.assigned_by = u2.id
                   ORDER BY (t.status = 'completed'), t.created_at DESC"""
            )
            return [Task.from_row(row) for row in cur.fetchall()]

    def list_for_user(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT t.*, u1.name AS assigned_to_name, u2.name AS assigned_by_name
                   FROM tasks t
                   JOIN users u1 ON t.assigned_to = u1.id
                   JOIN users u2 ON t.assigned_by = u2.id
                   WHERE t.assigned_to = %s
                   ORDER BY (t.status = 'completed'), t.created_at DESC""",
                (user_id,),
            )
            return [Task.from_row(row) for row in cur.fetchall()]

    def count_pending_for_user(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS total FROM tasks WHERE assigned_to = %s AND status = 'pending'",
                (user_id,),
            )
            return cur.fetchone()["total"]

    def mark_complete(self, task_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status = 'completed', completed_at = NOW() WHERE id = %s",
                (task_id,),
            )
        db.commit()

    def delete(self, task_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db.commit()
