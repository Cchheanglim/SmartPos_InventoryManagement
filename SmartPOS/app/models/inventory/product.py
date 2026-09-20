class Product:
    def __init__(self, id, name, category, price, quantity_in_stock, low_stock_threshold=5,
                 sku=None, cost=0, supplier_name=None, supplier_contact=None,
                 image_filename=None, image_url=None):
        self.id = id
        self.sku = sku
        self.name = name
        self.category = category
        self.price = price
        self.cost = cost
        self.quantity_in_stock = quantity_in_stock
        self.low_stock_threshold = low_stock_threshold
        self.supplier_name = supplier_name
        self.supplier_contact = supplier_contact
        self.image_filename = image_filename
        self.image_url = image_url

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.low_stock_threshold

    @property
    def display_image(self):
        """A locally uploaded file takes priority over an external URL,
        since it's guaranteed to still exist; falls back to the URL,
        and to None (category icon) if neither is set."""
        return self.image_filename or self.image_url or None

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row["id"],
            sku=row.get("sku"),
            name=row["name"],
            category=row.get("category"),
            price=row["price"],
            cost=row.get("cost", 0),
            quantity_in_stock=row["quantity_in_stock"],
            low_stock_threshold=row.get("low_stock_threshold", 5),
            supplier_name=row.get("supplier_name"),
            supplier_contact=row.get("supplier_contact"),
            image_filename=row.get("image_filename"),
            image_url=row.get("image_url"),
        )
