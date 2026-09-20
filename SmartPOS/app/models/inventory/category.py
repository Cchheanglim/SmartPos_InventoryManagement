class Category:
    DEFAULT_ICON = "fa-box"

    def __init__(self, id, name, description=None, icon=None):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon or self.DEFAULT_ICON

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(id=row["id"], name=row["name"], description=row.get("description"), icon=row.get("icon"))
