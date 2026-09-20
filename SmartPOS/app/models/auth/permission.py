class Permission:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def from_row(cls, row):
        return cls(id=row["id"], name=row["name"]) if row else None
