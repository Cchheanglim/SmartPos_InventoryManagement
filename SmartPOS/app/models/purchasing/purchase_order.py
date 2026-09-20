class PurchaseOrder:
    def __init__(self, id, product_id, quantity_ordered, status, ordered_by, ordered_at,
                 unit_cost=None, supplier_name=None, supplier_contact=None, received_by=None,
                 received_at=None, notes=None, product_name=None, ordered_by_name=None, received_by_name=None):
        self.id = id
        self.product_id = product_id
        self.quantity_ordered = quantity_ordered
        self.unit_cost = unit_cost
        self.status = status
        self.ordered_by = ordered_by
        self.ordered_at = ordered_at
        self.supplier_name = supplier_name
        self.supplier_contact = supplier_contact
        self.received_by = received_by
        self.received_at = received_at
        self.notes = notes
        self.product_name = product_name
        self.ordered_by_name = ordered_by_name
        self.received_by_name = received_by_name

    @property
    def is_pending(self):
        return self.status == "ordered"

    @property
    def total_cost(self):
        if self.unit_cost is None:
            return None
        return round(float(self.unit_cost) * self.quantity_ordered, 2)

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            product_id=row["product_id"],
            quantity_ordered=row["quantity_ordered"],
            unit_cost=row.get("unit_cost"),
            status=row["status"],
            ordered_by=row["ordered_by"],
            ordered_at=row["ordered_at"],
            supplier_name=row.get("supplier_name"),
            supplier_contact=row.get("supplier_contact"),
            received_by=row.get("received_by"),
            received_at=row.get("received_at"),
            notes=row.get("notes"),
            product_name=row.get("product_name"),
            ordered_by_name=row.get("ordered_by_name"),
            received_by_name=row.get("received_by_name"),
        )
