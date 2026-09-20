from app.extensions import get_db
from app.models.purchasing.purchase_order import PurchaseOrder


class PurchaseOrderRepository:
    """Only this class writes MySQL queries for purchase_orders."""

    def create(self, product_id, quantity_ordered, ordered_by, unit_cost=None, supplier_name=None,
               supplier_contact=None, notes=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO purchase_orders
                   (product_id, quantity_ordered, unit_cost, ordered_by, supplier_name, supplier_contact, notes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (product_id, quantity_ordered, unit_cost, ordered_by, supplier_name, supplier_contact, notes),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def total_spent_between(self, start_date, end_date):
        """Total money actually spent restocking (only orders marked
        RECEIVED count — an order that's cancelled or still pending
        hasn't been paid for)."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(unit_cost * quantity_ordered), 0) AS total_spent
                   FROM purchase_orders
                   WHERE status = 'received' AND DATE(received_at) BETWEEN %s AND %s""",
                (start_date, end_date),
            )
            return float(cur.fetchone()["total_spent"])

    def find_by_id(self, po_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT po.*, p.name AS product_name,
                          ou.name AS ordered_by_name, ru.name AS received_by_name
                   FROM purchase_orders po
                   JOIN products p ON po.product_id = p.id
                   JOIN users ou ON po.ordered_by = ou.id
                   LEFT JOIN users ru ON po.received_by = ru.id
                   WHERE po.id = %s""",
                (po_id,),
            )
            return PurchaseOrder.from_row(cur.fetchone())

    def list_all(self, status=None):
        db = get_db()
        query = """SELECT po.*, p.name AS product_name,
                          ou.name AS ordered_by_name, ru.name AS received_by_name
                   FROM purchase_orders po
                   JOIN products p ON po.product_id = p.id
                   JOIN users ou ON po.ordered_by = ou.id
                   LEFT JOIN users ru ON po.received_by = ru.id"""
        params = []
        if status:
            query += " WHERE po.status = %s"
            params.append(status)
        query += " ORDER BY po.ordered_at DESC"
        with db.cursor() as cur:
            cur.execute(query, params)
            return [PurchaseOrder.from_row(row) for row in cur.fetchall()]

    def mark_received(self, po_id, received_by):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """UPDATE purchase_orders
                   SET status = 'received', received_by = %s, received_at = NOW()
                   WHERE id = %s""",
                (received_by, po_id),
            )
        db.commit()

    def mark_cancelled(self, po_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE purchase_orders SET status = 'cancelled' WHERE id = %s", (po_id,))
        db.commit()
