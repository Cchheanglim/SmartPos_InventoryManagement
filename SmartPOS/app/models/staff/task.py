class Task:
    def __init__(self, id, title, description, assigned_to, assigned_by, status,
                 created_at, completed_at=None, assigned_to_name=None, assigned_by_name=None):
        self.id = id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.assigned_by = assigned_by
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at
        self.assigned_to_name = assigned_to_name
        self.assigned_by_name = assigned_by_name

    @property
    def is_completed(self):
        return self.status == "completed"

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            title=row["title"],
            description=row.get("description"),
            assigned_to=row["assigned_to"],
            assigned_by=row["assigned_by"],
            status=row["status"],
            created_at=row["created_at"],
            completed_at=row.get("completed_at"),
            assigned_to_name=row.get("assigned_to_name"),
            assigned_by_name=row.get("assigned_by_name"),
        )
