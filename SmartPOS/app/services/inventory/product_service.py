"""
Owns pure product CRUD and stock-related read queries, extracted from
InventoryService — product listing/creation/editing, manual stock
adjustment, and the inventory-value/restock-intelligence reports.
InventoryService keeps the same method names everything else already
calls (app/routes/inventory/product_routes.py is unchanged) and just
delegates to this internally, alongside StockAlertService and
PurchaseService (see those files) — InventoryService is now a thin
orchestrator composing all three rather than implementing any of it
itself.
"""
from app.repositories.inventory.product_repository import ProductRepository
from app.repositories.inventory.stock_repository import StockMovementRepository
from app.utils.telegram import TelegramService


class ProductService:
    def __init__(self, stock_alert_service):
        """stock_alert_service is passed in (not constructed here) so
        InventoryService's single StockAlertService instance is shared,
        rather than each service quietly having its own."""
        self.product_repo = ProductRepository()
        self.stock_repo = StockMovementRepository()
        self.telegram = TelegramService()
        self.stock_alert_service = stock_alert_service

    def list_products(self, search=None, category=None):
        return self.product_repo.list_all(search=search, category=category)

    def list_categories(self):
        return self.product_repo.list_categories()

    def get_product(self, product_id):
        return self.product_repo.find_by_id(product_id)

    def suggest_next_sku(self):
        return self.product_repo.suggest_next_sku()

    def create_product(self, name, category, price, quantity_in_stock, low_stock_threshold=5,
                        sku=None, cost=0, supplier_name=None, supplier_contact=None, image_filename=None):
        if price < 0:
            raise ValueError("Price cannot be negative.")
        if cost < 0:
            raise ValueError("Cost cannot be negative.")
        if quantity_in_stock < 0:
            raise ValueError("Initial stock cannot be negative.")
        return self.product_repo.create(
            name, category, price, quantity_in_stock, low_stock_threshold,
            sku=sku, cost=cost, supplier_name=supplier_name, supplier_contact=supplier_contact,
            image_filename=image_filename,
        )

    def update_product(self, product_id, name, category, price, low_stock_threshold,
                        sku=None, cost=0, supplier_name=None, supplier_contact=None, image_filename=None):
        if price < 0:
            raise ValueError("Price cannot be negative.")
        if cost < 0:
            raise ValueError("Cost cannot be negative.")
        self.product_repo.update(
            product_id, name, category, price, low_stock_threshold,
            sku=sku, cost=cost, supplier_name=supplier_name, supplier_contact=supplier_contact,
            image_filename=image_filename,
        )

    def delete_product(self, product_id):
        self.product_repo.delete(product_id)

    def adjust_stock_manually(self, product_id, change_amount, reason, staff_name=None):
        """
        Manual stock adjustment by an Inventory Manager or Admin
        (e.g. restock, damage, correction) — separate from the automatic
        deduction that SalesService triggers during checkout.
        """
        product = self.product_repo.find_by_id(product_id)
        if product is None:
            raise ValueError("Product not found.")
        if product.quantity_in_stock + change_amount < 0:
            raise ValueError("This adjustment would make stock negative.")
        self.product_repo.adjust_stock(product_id, change_amount)
        self.stock_repo.create(product_id, change_amount, reason)

        if change_amount > 0:
            self.telegram.notify_restock(product.name, change_amount, staff_name or "Unknown")
        self.stock_alert_service.check_and_alert(product_id)

    def low_stock_products(self):
        return [p for p in self.product_repo.list_all() if p.is_low_stock]

    def recent_stock_movements(self, limit=50):
        return self.stock_repo.list_recent(limit=limit)

    def total_inventory_value(self):
        return self.product_repo.total_inventory_value()

    def inventory_value_by_category(self):
        return self.product_repo.inventory_value_by_category()

    def restock_intelligence(self, category=None, search=None):
        return self.product_repo.restock_intelligence(category=category, search=search)
