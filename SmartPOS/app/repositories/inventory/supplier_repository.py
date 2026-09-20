from app.extensions import get_db
from app.models.inventory.supplier import Supplier
from app.repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository):
    table_name = "suppliers"
    model_class = Supplier

    def create(self, name, contact_name=None, phone=None, email=None, address=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO suppliers (name, contact_name, phone, email, address)
                   VALUES (%s, %s, %s, %s, %s)""",
                (name, contact_name, phone, email, address),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def update(self, supplier_id, name, contact_name=None, phone=None, email=None, address=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """UPDATE suppliers SET name = %s, contact_name = %s, phone = %s,
                   email = %s, address = %s WHERE id = %s""",
                (name, contact_name, phone, email, address, supplier_id),
            )
        db.commit()
