from app.repositories.staff.shift_repository import ShiftRepository
from app.repositories.auth.user_repository import UserRepository


class ShiftService:
    def __init__(self):
        self.shift_repo = ShiftRepository()
        self.user_repo = UserRepository()

    def list_shifts(self):
        return self.shift_repo.list_all(order_by="start_time")

    def get_shift(self, shift_id):
        return self.shift_repo.find_by_id(shift_id)

    def create_shift(self, name, start_time, end_time):
        name = (name or "").strip()
        if not name:
            raise ValueError("Shift name is required.")
        if not start_time or not end_time:
            raise ValueError("Start and end time are required.")
        if any(s.name == name for s in self.shift_repo.list_all()):
            raise ValueError(f'A shift template named "{name}" already exists.')
        return self.shift_repo.create(name, start_time, end_time)

    def update_shift(self, shift_id, name, start_time, end_time):
        name = (name or "").strip()
        if not name:
            raise ValueError("Shift name is required.")
        if not start_time or not end_time:
            raise ValueError("Start and end time are required.")
        if any(s.name == name and s.id != shift_id for s in self.shift_repo.list_all()):
            raise ValueError(f'A shift template named "{name}" already exists.')
        self.shift_repo.update(shift_id, name, start_time, end_time)

    def delete_shift(self, shift_id):
        # Assigning a shift template just copies its values onto the
        # user's own shift_name/shift_start/shift_end columns (see
        # ShiftTemplate's docstring) — there's no foreign key, so deleting
        # a template never changes anyone already assigned to it.
        self.shift_repo.delete(shift_id)

    def assign_shift_to_user(self, user_id, shift_id):
        shift = self.shift_repo.find_by_id(shift_id)
        if shift is None:
            raise ValueError("That shift template no longer exists.")
        self.user_repo.set_shift(user_id, shift.name, shift.start_time, shift.end_time)
