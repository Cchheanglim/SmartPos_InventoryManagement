class ShiftTemplate:
    """A reusable shift definition (e.g. "Morning", 06:00-14:00) that staff
    can be assigned to. Assigning one just copies its name/start/end onto
    the user's own shift_name/shift_start/shift_end columns (see
    UserRepository.set_shift) — it does not create a foreign-key link, so
    editing or deleting a template later never affects staff already
    assigned to it.
    """

    def __init__(self, id, name, start_time, end_time):
        self.id = id
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            start_time=row["start_time"],
            end_time=row["end_time"],
        )
