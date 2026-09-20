class Sale:
    def __init__(self, id, cashier_id, discount_percent, payment_method, total_amount,
                 created_at, tax_percent=0, cashier_name=None, customer_phone=None, items=None):
        self.id = id
        self.cashier_id = cashier_id
        self.discount_percent = discount_percent
        self.tax_percent = tax_percent
        self.payment_method = payment_method
        self.total_amount = total_amount
        self.created_at = created_at
        self.cashier_name = cashier_name
        self.customer_phone = customer_phone
        self.items = items or []

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            cashier_id=row["cashier_id"],
            discount_percent=row["discount_percent"],
            tax_percent=row.get("tax_percent", 0),
            payment_method=row["payment_method"],
            total_amount=row["total_amount"],
            created_at=row["created_at"],
            cashier_name=row.get("cashier_name"),
            customer_phone=row.get("customer_phone"),
        )
