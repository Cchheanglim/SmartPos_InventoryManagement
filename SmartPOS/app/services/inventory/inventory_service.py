from app.services.inventory.stock_alert_service import StockAlertService
from app.services.inventory.product_service import ProductService
from app.services.purchasing.purchase_service import PurchaseService


class InventoryService:
    """
    Thin orchestrator over the inventory domain — composes ProductService
    (product CRUD + stock), PurchaseService (purchase orders), and
    StockAlertService (low-stock alerting), keeping the same method names
    app/routes/inventory/product_routes.py already calls, so that file
    didn't need to change. All the actual business logic lives in those
    three services now; this class just routes to the right one.
    """

    def __init__(self):
        self.stock_alert_service = StockAlertService()
        self.product_service = ProductService(self.stock_alert_service)
        self.purchase_service = PurchaseService()

    # ---------- Products / stock — delegated to ProductService ----------

    def list_products(self, search=None, category=None):
        return self.product_service.list_products(search=search, category=category)

    def list_categories(self):
        return self.product_service.list_categories()

    def get_product(self, product_id):
        return self.product_service.get_product(product_id)

    def suggest_next_sku(self):
        return self.product_service.suggest_next_sku()

    def create_product(self, name, category, price, quantity_in_stock, low_stock_threshold=5,
                        sku=None, cost=0, supplier_name=None, supplier_contact=None, image_filename=None):
        return self.product_service.create_product(
            name, category, price, quantity_in_stock, low_stock_threshold=low_stock_threshold,
            sku=sku, cost=cost, supplier_name=supplier_name, supplier_contact=supplier_contact,
            image_filename=image_filename,
        )

    def update_product(self, product_id, name, category, price, low_stock_threshold,
                        sku=None, cost=0, supplier_name=None, supplier_contact=None, image_filename=None):
        self.product_service.update_product(
            product_id, name, category, price, low_stock_threshold,
            sku=sku, cost=cost, supplier_name=supplier_name, supplier_contact=supplier_contact,
            image_filename=image_filename,
        )

    def delete_product(self, product_id):
        self.product_service.delete_product(product_id)

    def adjust_stock_manually(self, product_id, change_amount, reason, staff_name=None):
        self.product_service.adjust_stock_manually(product_id, change_amount, reason, staff_name=staff_name)

    def check_low_stock_alert(self, product_id):
        self.stock_alert_service.check_and_alert(product_id)

    def low_stock_products(self):
        return self.product_service.low_stock_products()

    def recent_stock_movements(self, limit=50):
        return self.product_service.recent_stock_movements(limit=limit)

    def total_inventory_value(self):
        return self.product_service.total_inventory_value()

    def inventory_value_by_category(self):
        return self.product_service.inventory_value_by_category()

    def restock_intelligence(self, category=None, search=None):
        return self.product_service.restock_intelligence(category=category, search=search)

    # ---------- Purchase Orders / Restocking — delegated to PurchaseService ----------

    def create_purchase_order(self, product_id, quantity_ordered, staff_id, staff_name=None,
                               unit_cost=None, supplier_name=None, supplier_contact=None, notes=None):
        return self.purchase_service.create_purchase_order(
            product_id, quantity_ordered, staff_id, staff_name=staff_name,
            unit_cost=unit_cost, supplier_name=supplier_name,
            supplier_contact=supplier_contact, notes=notes,
        )

    def list_purchase_orders(self, status=None):
        return self.purchase_service.list_purchase_orders(status=status)

    def receive_purchase_order(self, po_id, staff_id, staff_name=None):
        self.purchase_service.receive_purchase_order(po_id, staff_id, staff_name=staff_name)

    def cancel_purchase_order(self, po_id):
        self.purchase_service.cancel_purchase_order(po_id)
