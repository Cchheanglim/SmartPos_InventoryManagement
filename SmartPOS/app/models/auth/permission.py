class Permission:
    def __init__(self, id, name, description=None, is_system=False):
        self.id = id
        self.name = name
        self.description = description or name.replace("_", " ").title()
        self.is_system = is_system

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
            description=row.get("description"),
            is_system=bool(row.get("is_system", False)),
        )

