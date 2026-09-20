class Notification:
    def __init__(self, id, user_id, message, category="general", is_read=False, created_at=None):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.category = category
        self.is_read = bool(is_read)
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            message=row["message"],
            category=row.get("category", "general"),
            is_read=row.get("is_read", False),
            created_at=row.get("created_at"),
        )
