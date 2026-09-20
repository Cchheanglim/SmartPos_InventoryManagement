from app.extensions import get_db
from app.models.inventory.category import Category
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository):
    table_name = "categories"
    model_class = Category

    def find_by_name(self, name):
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM categories WHERE name = %s", (name,))
            return Category.from_row(cur.fetchone())

    def create(self, name, description=None, icon=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO categories (name, description, icon) VALUES (%s, %s, %s)",
                (name, description, icon),
            )
            new_id = cur.lastrowid
        db.commit()
        return new_id

    def update(self, category_id, name, description=None, icon=None):
        db = get_db()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE categories SET name = %s, description = %s, icon = %s WHERE id = %s",
                (name, description, icon, category_id),
            )
        db.commit()

    def count_products_using(self, category_name):
        """Used to warn before deleting a category that's still in use —
        products.category is a plain text column (see schema.sql note),
        so this is a name match rather than a foreign key lookup."""
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM products WHERE category = %s", (category_name,))
            return cur.fetchone()["n"]
