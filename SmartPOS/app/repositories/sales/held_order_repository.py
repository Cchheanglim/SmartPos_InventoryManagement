import json

from app.extensions import get_db
from app.models.sales.held_order import HeldOrder


class HeldOrderRepository:
    """Only this class writes MySQL queries for held_orders."""

    def create(self, cashier_id, cart_items, discount_percent, customer_phone=None, customer_name=None, note=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO held_orders (cashier_id, cart_json, discount_percent, customer_phone, customer_name, note)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (cashier_id, json.dumps(cart_items), discount_percent, customer_phone, customer_name, note),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def find_by_id(self, held_order_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT h.*, u.name AS cashier_name FROM held_orders h
                   JOIN users u ON h.cashier_id = u.id
                   WHERE h.id = %s""",
                (held_order_id,),
            )
            return HeldOrder.from_row(cur.fetchone())

    def list_all(self):
        """
        Shows every held order regardless of who parked it — a shared
        checkout terminal means a different cashier may need to resume
        someone else's held cart after a shift change.
        """
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT h.*, u.name AS cashier_name FROM held_orders h
                   JOIN users u ON h.cashier_id = u.id
                   ORDER BY h.held_at DESC"""
            )
            return [HeldOrder.from_row(row) for row in cur.fetchall()]

    def delete(self, held_order_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("DELETE FROM held_orders WHERE id = %s", (held_order_id,))
        db.commit()

    def count_all(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM held_orders")
            return cur.fetchone()["total"]
