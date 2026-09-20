"""
Refund/void data access, extracted from the "Refunds / Voids" section of
SaleRepository (app/repositories/sales/sale_repository.py) — same
queries, moved out so refunds have their own repository the way the rest
of the domain-per-file plan intends. SaleRepository keeps thin
passthrough methods with the same names for any existing caller, so
nothing else needed to change.
"""
from app.extensions import get_db
from app.models.sales.refund import Refund
from app.models.sales.refund_item import RefundItem


class RefundRepository:
    def refunded_quantities_for_sale(self, sale_id):
        """Returns {sale_item_id: total_quantity_already_refunded} for
        every item on this sale — used to stop a refund from exceeding
        what was actually purchased."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT ri.sale_item_id, SUM(ri.quantity) AS refunded_qty
                   FROM refund_items ri
                   JOIN refunds r ON ri.refund_id = r.id
                   WHERE r.sale_id = %s
                   GROUP BY ri.sale_item_id""",
                (sale_id,),
            )
            return {row["sale_item_id"]: row["refunded_qty"] for row in cur.fetchall()}

    def create_refund_with_items(self, sale_id, processed_by, reason, refund_amount, items):
        """items: list of dicts {sale_item_id, quantity}. Returns the new refund id."""
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                """INSERT INTO refunds (sale_id, processed_by, reason, refund_amount)
                   VALUES (%s, %s, %s, %s)""",
                (sale_id, processed_by, reason, refund_amount),
            )
            refund_id = cur.lastrowid
            for item in items:
                cur.execute(
                    """INSERT INTO refund_items (refund_id, sale_item_id, quantity)
                       VALUES (%s, %s, %s)""",
                    (refund_id, item["sale_item_id"], item["quantity"]),
                )
            db.commit()
            return refund_id
        except Exception:
            db.rollback()
            raise
        finally:
            cur.close()

    def list_refunds_for_sale(self, sale_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT r.*, u.name AS processed_by_name FROM refunds r
                   JOIN users u ON r.processed_by = u.id
                   WHERE r.sale_id = %s ORDER BY r.created_at DESC""",
                (sale_id,),
            )
            refunds = [Refund.from_row(row) for row in cur.fetchall()]
            for refund in refunds:
                cur.execute(
                    """SELECT rfi.*, p.name AS product_name, si.unit_price
                       FROM refund_items rfi
                       JOIN sale_items si ON rfi.sale_item_id = si.id
                       JOIN products p ON si.product_id = p.id
                       WHERE rfi.refund_id = %s""",
                    (refund.id,),
                )
                refund.items = [RefundItem.from_row(row) for row in cur.fetchall()]
            return refunds

    def total_refunds_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(refund_amount), 0) AS total_refunds
                   FROM refunds WHERE DATE(created_at) BETWEEN %s AND %s""",
                (start_date, end_date),
            )
            return cur.fetchone()["total_refunds"]

    def list_refunds_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT r.*, u.name AS processed_by_name FROM refunds r
                   JOIN users u ON r.processed_by = u.id
                   WHERE DATE(r.created_at) BETWEEN %s AND %s
                   ORDER BY r.created_at DESC""",
                (start_date, end_date),
            )
            return [Refund.from_row(row) for row in cur.fetchall()]
