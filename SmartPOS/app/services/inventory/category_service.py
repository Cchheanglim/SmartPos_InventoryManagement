from app.repositories.inventory.category_repository import CategoryRepository
from app.repositories.inventory.product_repository import ProductRepository

# A curated whitelist rather than free text: keeps the icon always a real,
# renderable Font Awesome class (the icon font already loaded by the app),
# and gives the category form a friendly dropdown instead of asking
# whoever's adding a category to know CSS class names.
ICON_CHOICES = [
    ("fa-box", "Box (default)"),
    ("fa-cookie-bite", "Snacks"),
    ("fa-bottle-water", "Beverages"),
    ("fa-cheese", "Dairy"),
    ("fa-broom", "Household"),
    ("fa-pump-soap", "Personal Care"),
    ("fa-jar", "Pantry / Jarred goods"),
    ("fa-bread-slice", "Bakery"),
    ("fa-carrot", "Produce"),
    ("fa-drumstick-bite", "Meat"),
    ("fa-fish", "Seafood"),
    ("fa-snowflake", "Frozen"),
    ("fa-mortar-pestle", "Spices / Condiments"),
    ("fa-mug-hot", "Coffee / Tea"),
    ("fa-candy-cane", "Candy / Sweets"),
    ("fa-pills", "Health / Pharmacy"),
    ("fa-baby", "Baby care"),
    ("fa-paw", "Pet supplies"),
    ("fa-wine-bottle", "Alcohol"),
    ("fa-cannabis", "Tobacco"),
]
VALID_ICONS = {value for value, _ in ICON_CHOICES}


class CategoryInUseError(Exception):
    pass


class CategoryService:
    def __init__(self):
        self.category_repo = CategoryRepository()

    def list_categories(self):
        return self.category_repo.list_all(order_by="name")

    def get_category(self, category_id):
        return self.category_repo.find_by_id(category_id)

    def create_category(self, name, description=None, icon=None):
        name = (name or "").strip()
        if not name:
            raise ValueError("Category name is required.")
        if self.category_repo.find_by_name(name):
            raise ValueError(f'A category named "{name}" already exists.')
        icon = icon if icon in VALID_ICONS else None
        return self.category_repo.create(name, description, icon)

    def update_category(self, category_id, name, description=None, icon=None):
        name = (name or "").strip()
        if not name:
            raise ValueError("Category name is required.")
        existing = self.category_repo.find_by_name(name)
        if existing and existing.id != category_id:
            raise ValueError(f'A category named "{name}" already exists.')
        icon = icon if icon in VALID_ICONS else None

        old = self.category_repo.find_by_id(category_id)
        self.category_repo.update(category_id, name, description, icon)
        if old and old.name != name:
            # Move every product that was using the old name so they
            # aren't silently orphaned under a category that no longer exists.
            ProductRepository().reassign_category(old.name, name)

    def delete_category(self, category_id):
        category = self.category_repo.find_by_id(category_id)
        if category is None:
            return
        in_use = self.category_repo.count_products_using(category.name)
        if in_use > 0:
            raise CategoryInUseError(
                f'"{category.name}" is still used by {in_use} product(s). '
                "Reassign those products to a different category first."
            )
        self.category_repo.delete(category_id)
