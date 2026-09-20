class Supplier:
    def __init__(self, id, name, contact_name=None, phone=None, email=None,
                 address=None, created_at=None):
        self.id = id
        self.name = name
        self.contact_name = contact_name
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            contact_name=row.get("contact_name"),
            phone=row.get("phone"),
            email=row.get("email"),
            address=row.get("address"),
            created_at=row.get("created_at"),
        )
