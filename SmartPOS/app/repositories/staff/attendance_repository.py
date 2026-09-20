from app.extensions import get_db
from app.models.staff.attendance import Attendance


class AttendanceRepository:
    """Only this class writes MySQL queries for the attendance table."""

    def find_open_shift(self, user_id):
        """Returns the user's currently open (not-yet-clocked-out) shift, if any."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT * FROM attendance WHERE user_id = %s AND clock_out IS NULL ORDER BY clock_in DESC LIMIT 1",
                (user_id,),
            )
            return Attendance.from_row(cur.fetchone())

    def clock_in(self, user_id, starting_cash=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO attendance (user_id, clock_in, starting_cash) VALUES (%s, NOW(), %s)",
                (user_id, starting_cash),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def clock_out(self, attendance_id, counted_cash=None, expected_cash=None, cash_difference=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """UPDATE attendance
                   SET clock_out = NOW(), counted_cash = %s, expected_cash = %s, cash_difference = %s
                   WHERE id = %s""",
                (counted_cash, expected_cash, cash_difference, attendance_id),
            )
        db.commit()

    def find_by_id(self, attendance_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT a.*, u.name AS user_name FROM attendance a
                   JOIN users u ON a.user_id = u.id
                   WHERE a.id = %s""",
                (attendance_id,),
            )
            return Attendance.from_row(cur.fetchone())

    def list_for_user(self, user_id, limit=20):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT a.*, u.name AS user_name FROM attendance a
                   JOIN users u ON a.user_id = u.id
                   WHERE a.user_id = %s ORDER BY a.clock_in DESC LIMIT %s""",
                (user_id, limit),
            )
            return [Attendance.from_row(row) for row in cur.fetchall()]

    def list_recent(self, limit=50):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT a.*, u.name AS user_name FROM attendance a
                   JOIN users u ON a.user_id = u.id
                   ORDER BY a.clock_in DESC LIMIT %s""",
                (limit,),
            )
            return [Attendance.from_row(row) for row in cur.fetchall()]

    def currently_clocked_in_user_ids(self):
        """Used by Manage Staff to show a live In/Out status per person."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT DISTINCT user_id FROM attendance WHERE clock_out IS NULL")
            return {row["user_id"] for row in cur.fetchall()}
