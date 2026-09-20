"""
Tests for the admin "force close" safety net: an admin closing a
staff member's abandoned open shift so they aren't permanently locked
out of clocking in again. Uses a fake repository instead of a real
MySQL connection, so this runs without a database.

Run with: python -m pytest tests/
"""
import pytest
from datetime import datetime
from app.services.staff.attendance_service import AttendanceService


class FakeShift:
    def __init__(self, id, user_id, clock_in, clock_out=None):
        self.id = id
        self.user_id = user_id
        self.clock_in = clock_in
        self.clock_out = clock_out


class FakeAttendanceRepo:
    def __init__(self, shifts):
        self._shifts = {s.id: s for s in shifts}
        self._next_id = max(self._shifts.keys(), default=0) + 1
        self.closed_calls = []

    def find_by_id(self, attendance_id):
        return self._shifts.get(attendance_id)

    def find_open_shift(self, user_id):
        for s in self._shifts.values():
            if s.user_id == user_id and s.clock_out is None:
                return s
        return None

    def clock_in(self, user_id, starting_cash=None):
        shift = FakeShift(id=self._next_id, user_id=user_id, clock_in=datetime.now())
        self._shifts[shift.id] = shift
        self._next_id += 1
        return shift

    def clock_out(self, attendance_id, counted_cash=None, expected_cash=None, cash_difference=None):
        self.closed_calls.append((attendance_id, counted_cash, expected_cash, cash_difference))
        self._shifts[attendance_id].clock_out = datetime.now()


def make_service(shifts):
    service = AttendanceService()
    service.attendance_repo = FakeAttendanceRepo(shifts)
    return service


def test_force_close_closes_an_open_shift():
    service = make_service([FakeShift(id=1, user_id=5, clock_in=datetime.now())])
    service.admin_force_close(1)
    assert service.attendance_repo.find_by_id(1).clock_out is not None


def test_force_close_records_no_fabricated_cash_reconciliation():
    service = make_service([FakeShift(id=1, user_id=5, clock_in=datetime.now())])
    service.admin_force_close(1)
    call = service.attendance_repo.closed_calls[0]
    assert call == (1, None, None, None)


def test_force_close_rejects_already_closed_shift():
    service = make_service([
        FakeShift(id=1, user_id=5, clock_in=datetime.now(), clock_out=datetime.now())
    ])
    with pytest.raises(ValueError, match="already closed"):
        service.admin_force_close(1)


def test_force_close_rejects_unknown_shift():
    service = make_service([])
    with pytest.raises(ValueError, match="not found"):
        service.admin_force_close(999)


def test_clock_in_unblocked_after_force_close():
    """The actual bug this feature fixes: before force-close, a stuck-open
    shift permanently blocks that user from clocking in again."""
    service = make_service([FakeShift(id=1, user_id=5, clock_in=datetime.now())])

    with pytest.raises(ValueError, match="already clocked in"):
        service.clock_in(5)

    service.admin_force_close(1)

    new_shift = service.clock_in(5)  # no longer raises
    assert new_shift.user_id == 5
    assert new_shift.clock_out is None
