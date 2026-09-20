from app.extensions import get_db
from app.models.sales.sale import Sale
from app.models.sales.sale_item import SaleItem


class SaleRepository:
    """Only this class writes MySQL queries for sales and sale_items."""

    def create_sale_with_items(self, cashier_id, discount_percent, payment_method,
                                total_amount, line_items, tax_percent=0, customer_phone=None):
        """
        line_items: list of dicts {product_id, quantity, unit_price}
        Creates the sale row and all sale_item rows in a single transaction,
        so a sale is never left half-recorded. Returns the new sale id.
        """
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute(
                """INSERT INTO sales (cashier_id, discount_percent, tax_percent, payment_method, customer_phone, total_amount)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (cashier_id, discount_percent, tax_percent, payment_method, customer_phone, total_amount),
            )
            sale_id = cur.lastrowid

            for item in line_items:
                cur.execute(
                    """INSERT INTO sale_items (sale_id, product_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s)""",
                    (sale_id, item["product_id"], item["quantity"], item["unit_price"]),
                )
            db.commit()
            return sale_id
        except Exception:
            db.rollback()
            raise
        finally:
            cur.close()

    def find_by_id(self, sale_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT s.*, u.name AS cashier_name FROM sales s
                   JOIN users u ON s.cashier_id = u.id
                   WHERE s.id = %s""",
                (sale_id,),
            )
            sale = Sale.from_row(cur.fetchone())
            if sale is None:
                return None
            cur.execute(
                """SELECT si.*, p.name AS product_name FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   WHERE si.sale_id = %s""",
                (sale_id,),
            )
            sale.items = [SaleItem.from_row(row) for row in cur.fetchall()]
            return sale

    def list_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT s.*, u.name AS cashier_name FROM sales s
                   JOIN users u ON s.cashier_id = u.id
                   WHERE DATE(s.created_at) BETWEEN %s AND %s
                   ORDER BY s.created_at DESC""",
                (start_date, end_date),
            )
            return [Sale.from_row(row) for row in cur.fetchall()]

    def list_recent(self, limit=5, cashier_id=None):
        """Most recent sales, optionally scoped to one cashier — used on
        the personal dashboard rather than a fixed date range."""
        db = get_db()
        query = """SELECT s.*, u.name AS cashier_name FROM sales s
                   JOIN users u ON s.cashier_id = u.id"""
        params = []
        if cashier_id:
            query += " WHERE s.cashier_id = %s"
            params.append(cashier_id)
        query += " ORDER BY s.created_at DESC LIMIT %s"
        params.append(limit)
        with db.cursor() as cur:
            cur.execute(query, params)
            return [Sale.from_row(row) for row in cur.fetchall()]

    def search_history(self, sale_id=None, date=None, limit=50):
        """Powers the Sales History page — search by exact sale ID, filter
        by a specific date, or just show the most recent sales when
        neither is given."""
        db = get_db()
        with db.cursor() as cur:
            if sale_id:
                cur.execute(
                    """SELECT s.*, u.name AS cashier_name FROM sales s
                       JOIN users u ON s.cashier_id = u.id
                       WHERE s.id = %s""",
                    (sale_id,),
                )
            elif date:
                cur.execute(
                    """SELECT s.*, u.name AS cashier_name FROM sales s
                       JOIN users u ON s.cashier_id = u.id
                       WHERE DATE(s.created_at) = %s
                       ORDER BY s.created_at DESC""",
                    (date,),
                )
            else:
                cur.execute(
                    """SELECT s.*, u.name AS cashier_name FROM sales s
                       JOIN users u ON s.cashier_id = u.id
                       ORDER BY s.created_at DESC LIMIT %s""",
                    (limit,),
                )
            return [Sale.from_row(row) for row in cur.fetchall()]

    def daily_totals(self, days=7):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT DATE(created_at) AS sale_date,
                          COUNT(*) AS num_sales,
                          SUM(total_amount) AS total_revenue
                   FROM sales
                   WHERE created_at >= (CURDATE() - INTERVAL %s DAY)
                   GROUP BY DATE(created_at)
                   ORDER BY sale_date DESC""",
                (days,),
            )
            return cur.fetchall()

    def today_summary(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) AS num_sales, COALESCE(SUM(total_amount), 0) AS total_revenue
                   FROM sales WHERE DATE(created_at) = CURDATE()"""
            )
            return cur.fetchone()

    def today_summary_for_cashier(self, cashier_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) AS num_sales, COALESCE(SUM(total_amount), 0) AS total_revenue
                   FROM sales WHERE DATE(created_at) = CURDATE() AND cashier_id = %s""",
                (cashier_id,),
            )
            return cur.fetchone()

    def best_selling_products(self, limit=5):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT p.name, SUM(si.quantity) AS total_sold,
                          SUM(si.quantity * si.unit_price) AS total_revenue
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   GROUP BY p.id, p.name
                   ORDER BY total_sold DESC
                   LIMIT %s""",
                (limit,),
            )
            return cur.fetchall()

    def lowest_selling_products(self, limit=5):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT p.name, COALESCE(SUM(si.quantity), 0) AS total_sold,
                          COALESCE(SUM(si.quantity * si.unit_price), 0) AS total_revenue
                   FROM products p
                   LEFT JOIN sale_items si ON si.product_id = p.id
                   GROUP BY p.id, p.name
                   ORDER BY total_sold ASC
                   LIMIT %s""",
                (limit,),
            )
            return cur.fetchall()

    def revenue_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) AS num_sales, COALESCE(SUM(total_amount), 0) AS total_revenue
                   FROM sales WHERE DATE(created_at) BETWEEN %s AND %s""",
                (start_date, end_date),
            )
            return cur.fetchone()

    def cost_of_goods_sold_between(self, start_date, end_date):
        """Total cost of everything sold in the period — used as 'expenses' for Business Health."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(si.quantity * p.cost), 0) AS total_cost
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE DATE(s.created_at) BETWEEN %s AND %s""",
                (start_date, end_date),
            )
            return cur.fetchone()["total_cost"]

    def expense_by_category_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT p.category, COALESCE(SUM(si.quantity * p.cost), 0) AS total_cost
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE DATE(s.created_at) BETWEEN %s AND %s
                   GROUP BY p.category""",
                (start_date, end_date),
            )
            return cur.fetchall()

    def category_revenue_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT p.category, COALESCE(SUM(si.quantity * si.unit_price), 0) AS total_revenue
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE DATE(s.created_at) BETWEEN %s AND %s
                   GROUP BY p.category""",
                (start_date, end_date),
            )
            return cur.fetchall()

    def payment_method_breakdown_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT payment_method, COALESCE(SUM(total_amount), 0) AS total_revenue
                   FROM sales WHERE DATE(created_at) BETWEEN %s AND %s
                   GROUP BY payment_method""",
                (start_date, end_date),
            )
            return cur.fetchall()

    def revenue_trend_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT DATE(created_at) AS sale_date, COALESCE(SUM(total_amount), 0) AS total_revenue
                   FROM sales WHERE DATE(created_at) BETWEEN %s AND %s
                   GROUP BY DATE(created_at) ORDER BY sale_date""",
                (start_date, end_date),
            )
            return cur.fetchall()

    def cost_trend_between(self, start_date, end_date):
        """Per-day cost of goods sold — paired with revenue_trend_between
        to build the Revenue/Expense/Profit trend chart and daily report."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT DATE(s.created_at) AS sale_date,
                          COALESCE(SUM(si.quantity * p.cost), 0) AS total_cost
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE DATE(s.created_at) BETWEEN %s AND %s
                   GROUP BY DATE(s.created_at)""",
                (start_date, end_date),
            )
            return cur.fetchall()

    def daily_revenue_expense_profit_between(self, start_date, end_date):
        """
        Combines revenue and cost per day into one merged, date-sorted
        series — used by both the Revenue/Expense/Profit trend chart and
        the Daily Report bar chart, so both stay perfectly consistent.
        """
        revenue_rows = {row["sale_date"]: float(row["total_revenue"]) for row in self.revenue_trend_between(start_date, end_date)}
        cost_rows = {row["sale_date"]: float(row["total_cost"]) for row in self.cost_trend_between(start_date, end_date)}
        all_dates = sorted(set(revenue_rows.keys()) | set(cost_rows.keys()))

        return [
            {
                "date": d,
                "revenue": round(revenue_rows.get(d, 0.0), 2),
                "expense": round(cost_rows.get(d, 0.0), 2),
                "profit": round(revenue_rows.get(d, 0.0) - cost_rows.get(d, 0.0), 2),
            }
            for d in all_dates
        ]

    # ---------- Refunds / Voids ----------
    # Moved to app/repositories/sales/refund_repository.py (RefundRepository) —
    # SalesService now calls that directly instead of through here.

    # ---------- Shift cash reconciliation ----------

    def cash_sales_total_between(self, cashier_id, start_dt, end_dt):
        """Total of this cashier's completed cash sales during a shift window."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(total_amount), 0) AS total
                   FROM sales
                   WHERE cashier_id = %s AND payment_method = 'cash'
                     AND created_at BETWEEN %s AND %s""",
                (cashier_id, start_dt, end_dt),
            )
            return cur.fetchone()["total"]

    def cash_refunds_total_between(self, cashier_id, start_dt, end_dt):
        """Total refunded back out in cash (against cash sales this
        cashier processed) during a shift window — reduces expected cash."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(SUM(r.refund_amount), 0) AS total
                   FROM refunds r
                   JOIN sales s ON r.sale_id = s.id
                   WHERE s.payment_method = 'cash' AND r.processed_by = %s
                     AND r.created_at BETWEEN %s AND %s""",
                (cashier_id, start_dt, end_dt),
            )
            return cur.fetchone()["total"]
