class SaleItem:
    def __init__(self, id, sale_id, product_id, quantity, unit_price, product_name=None):
        self.id = id
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.product_name = product_name
        self.refunded_quantity = 0  # filled in separately by the refund form route

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    @property
    def refundable_quantity(self):
        return self.quantity - self.refunded_quantity

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            sale_id=row["sale_id"],
            product_id=row["product_id"],
            quantity=row["quantity"],
            unit_price=row["unit_price"],
            product_name=row.get("product_name"),
        )
