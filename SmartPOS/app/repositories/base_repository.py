"""
Optional generic CRUD helper. New, simple lookup-table repositories (like
CategoryRepository/SupplierRepository below) can inherit from this to
avoid repeating the same find/list/delete boilerplate. Existing
repositories were left as-is rather than retrofitted onto this base
class, since several of them have write paths that are deliberately NOT
generic (e.g. stock-affecting deletes, multi-table transactions) and
forcing them through a one-size-fits-all base risked changing behavior
that's already tested and working.
"""
from app.extensions import get_db


class BaseRepository:
    table_name = None   # override in subclass, e.g. "categories"
    model_class = None  # override in subclass, e.g. Category

    def find_by_id(self, id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table_name} WHERE id = %s", (id,))
            return self.model_class.from_row(cur.fetchone())

    def list_all(self, order_by="id"):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table_name} ORDER BY {order_by}")
            return [self.model_class.from_row(row) for row in cur.fetchall()]

    def delete(self, id):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))
        db.commit()
