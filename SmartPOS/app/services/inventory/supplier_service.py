from app.repositories.inventory.supplier_repository import SupplierRepository


class SupplierService:
    def __init__(self):
        self.supplier_repo = SupplierRepository()

    def list_suppliers(self):
        return self.supplier_repo.list_all(order_by="name")

    def get_supplier(self, supplier_id):
        return self.supplier_repo.find_by_id(supplier_id)

    def create_supplier(self, name, contact_name=None, phone=None, email=None, address=None):
        name = (name or "").strip()
        if not name:
            raise ValueError("Supplier name is required.")
        return self.supplier_repo.create(name, contact_name, phone, email, address)

    def update_supplier(self, supplier_id, name, contact_name=None, phone=None, email=None, address=None):
        name = (name or "").strip()
        if not name:
            raise ValueError("Supplier name is required.")
        self.supplier_repo.update(supplier_id, name, contact_name, phone, email, address)

    def delete_supplier(self, supplier_id):
        # Suppliers are only ever referenced by plain-text name/contact
        # columns on products and purchase_orders (see schema.sql note),
        # so unlike categories there's no foreign key to check — deleting
        # a supplier here never affects past purchase order records.
        self.supplier_repo.delete(supplier_id)
