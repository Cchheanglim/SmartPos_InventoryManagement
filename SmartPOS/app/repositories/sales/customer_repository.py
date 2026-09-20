from app.extensions import get_db
from app.models.sales.customer import Customer


class CustomerRepository:
    """Only this class writes MySQL queries for the customers table.
    Full phone numbers never leave this layer + CRMService; routes and
    templates only ever see the masked tag CRMService builds from this data.
    """

    def find_by_phone(self, phone):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM customers WHERE phone = %s", (phone,))
            return Customer.from_row(cur.fetchone())

    def create(self, phone, name):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO customers (phone, name) VALUES (%s, %s)",
                (phone, name),
            )
        db.commit()

    def total_count(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM customers")
            return cur.fetchone()["total"]

    def new_customers_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS total FROM customers WHERE join_date BETWEEN %s AND %s",
                (start_date, end_date),
            )
            return cur.fetchone()["total"]

    def sales_by_customer_between(self, start_date, end_date, limit=10):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT c.phone, c.name, COUNT(s.id) AS num_orders,
                          COALESCE(SUM(s.total_amount), 0) AS total_spent
                   FROM sales s
                   JOIN customers c ON s.customer_phone = c.phone
                   WHERE DATE(s.created_at) BETWEEN %s AND %s
                   GROUP BY c.phone, c.name
                   ORDER BY total_spent DESC
                   LIMIT %s""",
                (start_date, end_date, limit),
            )
            return cur.fetchall()

    def customer_vs_walkin_between(self, start_date, end_date):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT
                     SUM(CASE WHEN customer_phone IS NOT NULL THEN 1 ELSE 0 END) AS customer_orders,
                     SUM(CASE WHEN customer_phone IS NULL THEN 1 ELSE 0 END) AS walkin_orders,
                     COALESCE(SUM(CASE WHEN customer_phone IS NOT NULL THEN total_amount ELSE 0 END), 0) AS customer_revenue,
                     COALESCE(SUM(CASE WHEN customer_phone IS NULL THEN total_amount ELSE 0 END), 0) AS walkin_revenue
                   FROM sales WHERE DATE(created_at) BETWEEN %s AND %s""",
                (start_date, end_date),
            )
            return cur.fetchone()
