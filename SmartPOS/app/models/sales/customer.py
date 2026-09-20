class Customer:
    """
    The full phone number is stored here for internal lookups only.
    CRMService.build_masked_tag() is the only thing that should ever turn
    this into something shown in the UI (e.g. "Sara012").
    """
    def __init__(self, phone, name, join_date=None):
        self.phone = phone
        self.name = name
        self.join_date = join_date

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(phone=row["phone"], name=row["name"], join_date=row.get("join_date"))
