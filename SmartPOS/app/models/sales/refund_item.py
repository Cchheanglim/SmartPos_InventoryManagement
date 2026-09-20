class RefundItem:
    def __init__(self, id, refund_id, sale_item_id, quantity, product_name=None, unit_price=None):
        self.id = id
        self.refund_id = refund_id
        self.sale_item_id = sale_item_id
        self.quantity = quantity
        self.product_name = product_name
        self.unit_price = unit_price

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            refund_id=row["refund_id"],
            sale_item_id=row["sale_item_id"],
            quantity=row["quantity"],
            product_name=row.get("product_name"),
            unit_price=row.get("unit_price"),
        )
