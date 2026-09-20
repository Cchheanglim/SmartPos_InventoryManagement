class Refund:
    def __init__(self, id, sale_id, processed_by, reason, refund_amount, created_at,
                 processed_by_name=None, items=None):
        self.id = id
        self.sale_id = sale_id
        self.processed_by = processed_by
        self.reason = reason
        self.refund_amount = refund_amount
        self.created_at = created_at
        self.processed_by_name = processed_by_name
        self.items = items or []

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            sale_id=row["sale_id"],
            processed_by=row["processed_by"],
            reason=row.get("reason"),
            refund_amount=row["refund_amount"],
            created_at=row["created_at"],
            processed_by_name=row.get("processed_by_name"),
        )
