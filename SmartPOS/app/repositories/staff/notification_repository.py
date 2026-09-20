from app.extensions import get_db
from app.models.staff.notification import Notification


class NotificationRepository:
    def create(self, user_id, message, category="general"):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO notifications (user_id, message, category) VALUES (%s, %s, %s)",
                (user_id, message, category),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def create_for_users(self, user_ids, message, category="general"):
        """Fan the same notification out to several users at once (e.g.
        every user with manage_products permission, for a low-stock alert)."""
        db = get_db()
        with db.cursor() as cur:
            cur.executemany(
                "INSERT INTO notifications (user_id, message, category) VALUES (%s, %s, %s)",
                [(uid, message, category) for uid in user_ids],
            )
        db.commit()

    def list_for_user(self, user_id, unread_only=False, limit=50):
        db = get_db()
        query = "SELECT * FROM notifications WHERE user_id = %s"
        params = [user_id]
        if unread_only:
            query += " AND is_read = 0"
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        with db.cursor() as cur:
            cur.execute(query, params)
            return [Notification.from_row(row) for row in cur.fetchall()]

    def count_unread(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS n FROM notifications WHERE user_id = %s AND is_read = 0",
                (user_id,),
            )
            return cur.fetchone()["n"]

    def mark_read(self, notification_id, user_id):
        """Scoped to user_id too, so one user can't mark another's notification read."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s",
                (notification_id, user_id),
            )
        db.commit()

    def mark_all_read(self, user_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0",
                (user_id,),
            )
        db.commit()
