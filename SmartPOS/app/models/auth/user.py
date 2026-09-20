from flask_login import UserMixin


class User(UserMixin):
    """
    Domain model for a system user. Every Admin, Admin Assistant,
    Inventory Manager, and Cashier is a User distinguished only by
    role_id — role-specific behavior is expressed through permissions,
    not through separate subclasses at the persistence layer.
    """

    def __init__(self, id, name, email, password_hash, role_id, role_name,
                 phone=None, profile_picture=None, shift_name=None, shift_start=None,
                 shift_end=None, is_active=True, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.role_id = role_id
        self.role_name = role_name
        self.profile_picture = profile_picture
        self.shift_name = shift_name
        self.shift_start = shift_start
        self.shift_end = shift_end
        self._is_active = is_active
        self.created_at = created_at

    # Flask-Login required properties
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return bool(self._is_active)

    @property
    def has_shift_assigned(self):
        return bool(self.shift_name)

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            phone=row.get("phone"),
            password_hash=row["password_hash"],
            role_id=row["role_id"],
            role_name=row.get("role_name"),
            profile_picture=row.get("profile_picture"),
            shift_name=row.get("shift_name"),
            shift_start=row.get("shift_start"),
            shift_end=row.get("shift_end"),
            is_active=row.get("is_active", 1),
            created_at=row.get("created_at"),
        )
