from app.extensions import get_db
from app.models.inventory.product import Product


class ProductRepository:
    """Only this class writes MySQL queries for the products table."""

    def find_by_id(self, product_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return Product.from_row(cur.fetchone())

    def find_by_sku(self, sku):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM products WHERE sku = %s", (sku,))
            return Product.from_row(cur.fetchone())

    def list_all(self, search=None, category=None):
        db = get_db()
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        if search:
            query += " AND (name LIKE %s OR sku LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        if category:
            query += " AND category = %s"
            params.append(category)
        query += " ORDER BY name"
        with db.cursor() as cur:
            cur.execute(query, params)
            return [Product.from_row(row) for row in cur.fetchall()]

    def reassign_category(self, old_name, new_name):
        """Called when a category is renamed, so products already
        assigned to it move with the rename instead of being silently
        orphaned under a name that no longer exists in the categories
        table (products.category is a plain text column, not a foreign
        key — see schema.sql's note on why)."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE products SET category = %s WHERE category = %s", (new_name, old_name))
        db.commit()

    def list_categories(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
            )
            return [row["category"] for row in cur.fetchall()]

    def set_image_url_by_sku(self, sku, image_url):
        """Bulk-import helper — sets image_url for a product identified by
        its SKU rather than its internal id, matching how the original
        source data is keyed (PRD-001, PRD-002, ...)."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE products SET image_url = %s WHERE sku = %s", (image_url, sku))
            affected = cur.rowcount
        db.commit()
        return affected

    def set_supplier_by_sku(self, sku, supplier_name, supplier_contact):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE products SET supplier_name = %s, supplier_contact = %s WHERE sku = %s",
                (supplier_name, supplier_contact, sku),
            )
            affected = cur.rowcount
        db.commit()
        return affected

    def set_cost_by_sku(self, sku, cost):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE products SET cost = %s WHERE sku = %s", (cost, sku))
            affected = cur.rowcount
        db.commit()
        return affected

    def create(self, name, category, price, quantity_in_stock, low_stock_threshold=5,
               sku=None, cost=0, supplier_name=None, supplier_contact=None, image_filename=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """INSERT INTO products
                   (sku, name, category, price, cost, quantity_in_stock, low_stock_threshold,
                    supplier_name, supplier_contact, image_filename)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (sku, name, category, price, cost, quantity_in_stock, low_stock_threshold,
                 supplier_name, supplier_contact, image_filename),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def update(self, product_id, name, category, price, low_stock_threshold,
               sku=None, cost=0, supplier_name=None, supplier_contact=None, image_filename=None):
        db = get_db()
        with db.cursor() as cur:
            if image_filename is not None:
                cur.execute(
                    """UPDATE products SET name=%s, category=%s, price=%s, cost=%s, low_stock_threshold=%s,
                       sku=%s, supplier_name=%s, supplier_contact=%s, image_filename=%s
                       WHERE id=%s""",
                    (name, category, price, cost, low_stock_threshold, sku, supplier_name,
                     supplier_contact, image_filename, product_id),
                )
            else:
                cur.execute(
                    """UPDATE products SET name=%s, category=%s, price=%s, cost=%s, low_stock_threshold=%s,
                       sku=%s, supplier_name=%s, supplier_contact=%s
                       WHERE id=%s""",
                    (name, category, price, cost, low_stock_threshold, sku, supplier_name,
                     supplier_contact, product_id),
                )
        db.commit()

    def update_cost(self, product_id, cost):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE products SET cost = %s WHERE id = %s", (cost, product_id))
        db.commit()

    def delete(self, product_id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db.commit()

    def suggest_next_sku(self):
        """Mirrors the original system's PRD-XXX auto-numbering."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT sku FROM products WHERE sku LIKE 'PRD-%'")
            max_num = 0
            for row in cur.fetchall():
                digits = "".join(ch for ch in row["sku"] if ch.isdigit())
                if digits:
                    max_num = max(max_num, int(digits))
            return f"PRD-{max_num + 1:03d}"

    def adjust_stock(self, product_id, change_amount, cursor=None):
        """
        Adjusts stock by change_amount (negative to deduct, positive to add).
        Accepts an optional existing cursor so callers (e.g. SalesService) can
        run this inside a larger transaction instead of committing separately.
        """
        db = get_db()
        own_cursor = cursor is None
        cur = cursor or db.cursor()
        cur.execute(
            "UPDATE products SET quantity_in_stock = quantity_in_stock + %s WHERE id = %s",
            (change_amount, product_id),
        )
        if own_cursor:
            db.commit()
            cur.close()

    def total_inventory_value(self):
        """Current stock valued at cost — used on Business Health."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(quantity_in_stock * cost), 0) AS total_value FROM products")
            return cur.fetchone()["total_value"]

    def inventory_value_by_category(self):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                """SELECT COALESCE(category, 'Uncategorized') AS category,
                          COALESCE(SUM(quantity_in_stock * cost), 0) AS total_value
                   FROM products
                   GROUP BY category
                   ORDER BY total_value DESC"""
            )
            return cur.fetchall()

    def restock_intelligence(self, category=None, search=None):
        """Products with their units sold (all-time), current stock, and a
        recommended restock quantity (2x threshold minus current stock)."""
        db = get_db()
        query = """
            SELECT p.id, p.name, p.category, p.quantity_in_stock, p.low_stock_threshold,
                   COALESCE(SUM(si.quantity), 0) AS units_sold
            FROM products p
            LEFT JOIN sale_items si ON si.product_id = p.id
            WHERE 1=1
        """
        params = []
        if category:
            query += " AND p.category = %s"
            params.append(category)
        if search:
            query += " AND (p.name LIKE %s OR p.sku LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " GROUP BY p.id, p.name, p.category, p.quantity_in_stock, p.low_stock_threshold ORDER BY units_sold DESC"
        with db.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
