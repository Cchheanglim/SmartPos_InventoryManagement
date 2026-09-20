from app.extensions import get_db
from app.models.inventory.stock_movement import StockMovement


class StockMovementRepository:
    def create(self, product_id, change_amount, reason, cursor=None):
        db = get_db()
        own_cursor = cursor is None
        cur = cursor or db.cursor()
        cur.execute(
            """INSERT INTO stock_movements (product_id, change_amount, reason)
               VALUES (%s, %s, %s)""",
            (product_id, change_amount, reason),
        )
        if own_cursor:
            db.commit()
            cur.close()

    def list_for_product(self, product_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT sm.*, p.name AS product_name FROM stock_movements sm
                   JOIN products p ON sm.product_id = p.id
                   WHERE sm.product_id = %s ORDER BY sm.created_at DESC""",
                (product_id,),
            )
            return [StockMovement.from_row(row) for row in cur.fetchall()]

    def list_recent(self, limit=50):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT sm.*, p.name AS product_name FROM stock_movements sm
                   JOIN products p ON sm.product_id = p.id
                   ORDER BY sm.created_at DESC LIMIT %s""",
                (limit,),
            )
            return [StockMovement.from_row(row) for row in cur.fetchall()]
