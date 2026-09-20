class StockMovement:
    def __init__(self, id, product_id, change_amount, reason, created_at, product_name=None):
        self.id = id
        self.product_id = product_id
        self.change_amount = change_amount
        self.reason = reason
        self.created_at = created_at
        self.product_name = product_name

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            product_id=row["product_id"],
            change_amount=row["change_amount"],
            reason=row["reason"],
            created_at=row["created_at"],
            product_name=row.get("product_name"),
        )
