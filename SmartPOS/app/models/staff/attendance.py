from datetime import datetime


class Attendance:
    def __init__(self, id, user_id, clock_in, clock_out=None, user_name=None,
                 starting_cash=None, counted_cash=None, expected_cash=None, cash_difference=None):
        self.id = id
        self.user_id = user_id
        self.clock_in = clock_in
        self.clock_out = clock_out
        self.user_name = user_name
        self.starting_cash = starting_cash
        self.counted_cash = counted_cash
        self.expected_cash = expected_cash
        self.cash_difference = cash_difference

    @property
    def is_open(self):
        """True if this shift is still ongoing (no clock-out yet)."""
        return self.clock_out is None

    @property
    def duration_hours(self):
        """Hours worked so far — up to now if still clocked in."""
        end = self.clock_out or datetime.now()
        delta = end - self.clock_in
        return round(delta.total_seconds() / 3600, 2)

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            clock_in=row["clock_in"],
            clock_out=row.get("clock_out"),
            user_name=row.get("user_name"),
            starting_cash=row.get("starting_cash"),
            counted_cash=row.get("counted_cash"),
            expected_cash=row.get("expected_cash"),
            cash_difference=row.get("cash_difference"),
        )
