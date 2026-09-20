from datetime import datetime
from app.repositories.staff.attendance_repository import AttendanceRepository


class AttendanceService:
    """Owns the clock in/out business rule: a user can only have one open
    shift at a time — clocking in again while already clocked in, or
    clocking out with nothing open, are both rejected here."""

    def __init__(self):
        self.attendance_repo = AttendanceRepository()

    def get_status(self, user_id):
        """Returns the open Attendance row if the user is currently
        clocked in, or None if they're clocked out."""
        return self.attendance_repo.find_open_shift(user_id)

    def clock_in(self, user_id, starting_cash=None):
        if self.attendance_repo.find_open_shift(user_id) is not None:
            raise ValueError("You're already clocked in.")
        return self.attendance_repo.clock_in(user_id, starting_cash=starting_cash)

    def clock_out(self, user_id, counted_cash=None):
        """
        If counted_cash is given, reconciles the drawer: expected cash is
        the starting float plus every cash sale this cashier rang up
        during the shift, minus any cash refunds they processed. The
        difference (counted - expected) is stored so an Admin can review
        over/short shifts later — it's informational, never blocks
        clocking out.
        """
        open_shift = self.attendance_repo.find_open_shift(user_id)
        if open_shift is None:
            raise ValueError("You're not currently clocked in.")

        expected_cash = None
        cash_difference = None
        if counted_cash is not None:
            # Imported here (not at module level) to avoid a service-to-service
            # import cycle, since SalesService also depends on other repos.
            from app.repositories.sales.sale_repository import SaleRepository
            sale_repo = SaleRepository()
            now = datetime.now()
            cash_sales = sale_repo.cash_sales_total_between(user_id, open_shift.clock_in, now)
            cash_refunds = sale_repo.cash_refunds_total_between(user_id, open_shift.clock_in, now)
            starting = float(open_shift.starting_cash or 0)
            expected_cash = round(starting + float(cash_sales) - float(cash_refunds), 2)
            cash_difference = round(float(counted_cash) - expected_cash, 2)

        self.attendance_repo.clock_out(
            open_shift.id, counted_cash=counted_cash,
            expected_cash=expected_cash, cash_difference=cash_difference,
        )
        return self.attendance_repo.find_by_id(open_shift.id)

    def admin_force_close(self, attendance_id):
        """
        Closes a stuck-open shift on the staff member's behalf — e.g. they
        forgot to clock out and are now locked out of clocking in again
        (clock_in() refuses a second open shift for the same user). No
        cash reconciliation is attempted here: we can't retroactively
        know what the drawer looked like, so counted/expected/difference
        are left NULL rather than guessed at. Admin-only; gated by
        manage_users at the route level.
        """
        shift = self.attendance_repo.find_by_id(attendance_id)
        if shift is None:
            raise ValueError("Attendance record not found.")
        if shift.clock_out is not None:
            raise ValueError("That shift is already closed.")
        self.attendance_repo.clock_out(attendance_id, counted_cash=None, expected_cash=None, cash_difference=None)

    def history_for_user(self, user_id, limit=20):
        return self.attendance_repo.list_for_user(user_id, limit=limit)

    def recent_all(self, limit=50):
        return self.attendance_repo.list_recent(limit=limit)

    def currently_clocked_in_user_ids(self):
        return self.attendance_repo.currently_clocked_in_user_ids()
