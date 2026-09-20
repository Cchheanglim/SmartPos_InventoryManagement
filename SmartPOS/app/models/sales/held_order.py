import json


class HeldOrder:
    def __init__(self, id, cashier_id, cart_json, discount_percent, held_at,
                 customer_phone=None, customer_name=None, note=None, cashier_name=None):
        self.id = id
        self.cashier_id = cashier_id
        self.cart_json = cart_json
        self.discount_percent = discount_percent
        self.customer_phone = customer_phone
        self.customer_name = customer_name
        self.note = note
        self.held_at = held_at
        self.cashier_name = cashier_name

    @property
    def cart_items(self):
        """Decoded cart — a list of {product_id, name, price, quantity}."""
        return json.loads(self.cart_json)

    @property
    def item_count(self):
        return sum(item.get("quantity", 0) for item in self.cart_items)

    @property
    def estimated_total(self):
        subtotal = sum(item.get("price", 0) * item.get("quantity", 0) for item in self.cart_items)
        return round(subtotal * (1 - float(self.discount_percent) / 100), 2)

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            cashier_id=row["cashier_id"],
            cart_json=row["cart_json"],
            discount_percent=row["discount_percent"],
            customer_phone=row.get("customer_phone"),
            customer_name=row.get("customer_name"),
            note=row.get("note"),
            held_at=row["held_at"],
            cashier_name=row.get("cashier_name"),
        )
