"""
Owns the purchase-order / restocking workflow, extracted from the
"Purchase Orders / Restocking workflow" section of InventoryService
(app/services/inventory/inventory_service.py). InventoryService keeps the
same four method names (create_purchase_order, list_purchase_orders,
receive_purchase_order, cancel_purchase_order) and just delegates to this
internally — app/routes/inventory/product_routes.py is unchanged.

Still called through InventoryService rather than directly, since a
purchase order genuinely does need product data (default cost/supplier,
stock updates on receipt) — this split is about giving purchasing its
own single responsibility, not pretending it has zero relationship to
products.
"""
from app.repositories.inventory.product_repository import ProductRepository
from app.repositories.inventory.stock_repository import StockMovementRepository
from app.repositories.purchasing.purchase_order_repository import PurchaseOrderRepository
from app.utils.telegram import TelegramService


class PurchaseService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.stock_repo = StockMovementRepository()
        self.po_repo = PurchaseOrderRepository()
        self.telegram = TelegramService()

    def create_purchase_order(self, product_id, quantity_ordered, staff_id, staff_name=None,
                               unit_cost=None, supplier_name=None, supplier_contact=None, notes=None):
        """
        Formally records "ordered N units, awaiting delivery" — separate
        from adjust_stock_manually, which changes stock immediately. Stock
        only actually changes once the order is received.
        Defaults to the product's own supplier info / cost when not overridden.
        """
        product = self.product_repo.find_by_id(product_id)
        if product is None:
            raise ValueError("Product not found.")
        if quantity_ordered <= 0:
            raise ValueError("Quantity ordered must be positive.")

        supplier_name = supplier_name or product.supplier_name
        supplier_contact = supplier_contact or product.supplier_contact
        unit_cost = unit_cost if unit_cost is not None else product.cost

        po_id = self.po_repo.create(
            product_id, quantity_ordered, staff_id, unit_cost=unit_cost,
            supplier_name=supplier_name, supplier_contact=supplier_contact, notes=notes,
        )
        try:
            self.telegram.notify_purchase_order(product.name, quantity_ordered, supplier_name, staff_name or "Unknown")
        except Exception:
            pass  # A notification failure should never break the order.
        return po_id

    def list_purchase_orders(self, status=None):
        return self.po_repo.list_all(status=status)

    def receive_purchase_order(self, po_id, staff_id, staff_name=None):
        """Marks the order received AND adds the stock in one step — this
        is the only thing that actually changes quantity_in_stock for a PO."""
        po = self.po_repo.find_by_id(po_id)
        if po is None:
            raise ValueError("Purchase order not found.")
        if po.status != "ordered":
            raise ValueError(f"This purchase order is already {po.status}.")

        self.po_repo.mark_received(po_id, staff_id)
        self.product_repo.adjust_stock(po.product_id, po.quantity_ordered)
        self.stock_repo.create(po.product_id, po.quantity_ordered, reason=f"Purchase Order #{po_id} received")
        if po.unit_cost is not None:
            # Keep the product's own cost current so profit/margin reports
            # (which read products.cost) reflect what you're actually
            # paying now, not whatever it was set to when first created.
            self.product_repo.update_cost(po.product_id, po.unit_cost)
        try:
            self.telegram.notify_restock(po.product_name, po.quantity_ordered, staff_name or "Unknown")
        except Exception:
            pass

    def cancel_purchase_order(self, po_id):
        po = self.po_repo.find_by_id(po_id)
        if po is None:
            raise ValueError("Purchase order not found.")
        if po.status != "ordered":
            raise ValueError(f"This purchase order is already {po.status}.")
        self.po_repo.mark_cancelled(po_id)
