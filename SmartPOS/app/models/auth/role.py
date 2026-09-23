class Role:
    def __init__(self, id, name, user_count=0):
        self.id = id
        self.name = name
        self.user_count = user_count

    @property
    def display_name(self):
        return self.name.replace("_", " ").title()

    @classmethod
    def from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            user_count=row.get("user_count", 0)
        )

