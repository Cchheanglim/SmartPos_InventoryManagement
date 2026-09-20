"""
Owns the low-stock alerting rule, extracted from
InventoryService.check_low_stock_alert so it has its own single
responsibility (deciding *whether* and *who* to alert) separate from
InventoryService's job of owning product/stock data. InventoryService
now just delegates to this; the trigger points (after a manual
adjustment, and after checkout deducts stock) didn't change.
"""
from app.repositories.inventory.product_repository import ProductRepository
from app.utils.telegram import TelegramService


class StockAlertService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.telegram = TelegramService()

    def check_and_alert(self, product_id):
        """Re-reads the product's current stock and, if it's at or below
        its threshold, fires both a Telegram alert and an in-app
        notification (to everyone with manage_products)."""
        product = self.product_repo.find_by_id(product_id)
        if product is None:
            return
        if product.quantity_in_stock > product.low_stock_threshold:
            return

        reorder_qty = max(product.low_stock_threshold * 2 - product.quantity_in_stock, 0)
        self.telegram.notify_low_stock(
            product.name, product.quantity_in_stock, reorder_qty,
            product.supplier_name, product.supplier_contact,
        )

        # Imported here (not at module level) to avoid a circular import —
        # notification_service depends on auth_service, and several
        # services already import this module at app startup.
        from app.services.notifications.notification_service import NotificationService
        NotificationService().notify_users_with_permission(
            "manage_products",
            f'Low stock: "{product.name}" is down to {product.quantity_in_stock} '
            f"(threshold {product.low_stock_threshold}).",
            category="low_stock",
        )
