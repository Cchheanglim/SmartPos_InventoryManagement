from app.repositories.inventory.product_repository import ProductRepository
from app.repositories.sales.sale_repository import SaleRepository
from app.repositories.sales.refund_repository import RefundRepository
from app.repositories.inventory.stock_repository import StockMovementRepository
from app.services.sales.crm_service import CRMService
from app.services.sales.refund_service import RefundService
from app.utils.telegram import TelegramService
from app.utils.barcode import generate_payment_qr


class InsufficientStockError(Exception):
    def __init__(self, product_name, requested, available):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Not enough stock for '{product_name}': requested {requested}, only {available} available."
        )


class SalesService:
    """
    Owns the checkout workflow. This is the one place in the system that
    is allowed to decide whether a sale can complete — it validates
    stock, applies the discount, records the sale, triggers the matching
    stock deduction, resolves an optional customer phone through CRMService,
    and fires Telegram notifications, all as one unit of work.
    """

    def __init__(self):
        self.product_repo = ProductRepository()
        self.sale_repo = SaleRepository()
        self.refund_repo = RefundRepository()
        self.stock_repo = StockMovementRepository()
        self.refund_service = RefundService()
        self.crm_service = CRMService()
        self.telegram = TelegramService()

    def checkout(self, cashier_id, cart_items, discount_percent=0, tax_percent=0, payment_method="cash",
                 customer_phone=None, customer_name=None, cashier_name=None):
        """
        cart_items: list of dicts {product_id, quantity}
        customer_phone/customer_name: optional — if a phone is given and no
        matching customer exists, one is registered on the spot (requires
        customer_name in that case), matching a quick-add-at-register flow.
        Validates stock for every line BEFORE writing anything, so a
        checkout either fully succeeds or fails with no partial effect.

        Tax is applied AFTER the discount, on the discounted subtotal —
        the standard order of operations (discount first, then tax on
        what's actually being paid).
        """
        if not cart_items:
            raise ValueError("Cannot check out an empty cart.")
        if not (0 <= discount_percent <= 100):
            raise ValueError("Discount percent must be between 0 and 100.")
        if tax_percent < 0:
            raise ValueError("Tax percent cannot be negative.")

        resolved_phone = self._resolve_customer(customer_phone, customer_name)

        line_items = []
        subtotal = 0
        products_by_id = {}

        # Validate stock availability for every line first.
        for item in cart_items:
            product = self.product_repo.find_by_id(item["product_id"])
            if product is None:
                raise ValueError(f"Product {item['product_id']} not found.")
            quantity = int(item["quantity"])
            if quantity <= 0:
                raise ValueError(f"Quantity for '{product.name}' must be positive.")
            if quantity > product.quantity_in_stock:
                raise InsufficientStockError(product.name, quantity, product.quantity_in_stock)

            unit_price = float(product.price)
            line_items.append({
                "product_id": product.id,
                "quantity": quantity,
                "unit_price": unit_price,
            })
            subtotal += unit_price * quantity
            products_by_id[product.id] = product

        discounted_subtotal = subtotal * (1 - discount_percent / 100)
        total_amount = round(discounted_subtotal * (1 + tax_percent / 100), 2)

        # Record the sale and its line items as one transaction.
        sale_id = self.sale_repo.create_sale_with_items(
            cashier_id=cashier_id,
            discount_percent=discount_percent,
            tax_percent=tax_percent,
            payment_method=payment_method,
            total_amount=total_amount,
            line_items=line_items,
            customer_phone=resolved_phone,
        )

        # Deduct stock, log a movement, and check for a low-stock alert
        # for each product sold.
        for item in line_items:
            self.product_repo.adjust_stock(item["product_id"], -item["quantity"])
            self.stock_repo.create(
                item["product_id"], -item["quantity"], reason=f"Sale #{sale_id}"
            )

        self._notify_new_transaction(sale_id, total_amount, line_items, products_by_id, cashier_name)
        self._check_low_stock_after_sale(line_items)

        return self.sale_repo.find_by_id(sale_id)

    def _resolve_customer(self, customer_phone, customer_name):
        """Looks up an existing customer by phone, or registers a new one
        on the spot if a name was also provided. Returns the clean phone
        digits to store on the sale, or None for a walk-in with no phone."""
        if not customer_phone:
            return None
        existing = self.crm_service.find_or_none(customer_phone)
        if existing is not None:
            return existing.phone
        if customer_name:
            result = self.crm_service.register(customer_name, customer_phone)
            return result["phone"]
        # Phone given but not recognized and no name to register with —
        # treat as a walk-in rather than fail the whole sale.
        return None

    def _notify_new_transaction(self, sale_id, total_amount, line_items, products_by_id, cashier_name):
        item_summary = ", ".join(
            f"{products_by_id[i['product_id']].name} (x{i['quantity']})" for i in line_items
        )
        try:
            self.telegram.notify_new_transaction(sale_id, total_amount, item_summary, cashier_name or "Unknown")
        except Exception:
            pass  # A notification failure should never break a completed sale.

    def _check_low_stock_after_sale(self, line_items):
        from app.services.inventory.inventory_service import InventoryService
        inventory_service = InventoryService()
        for item in line_items:
            try:
                inventory_service.check_low_stock_alert(item["product_id"])
            except Exception:
                pass

    def generate_qr_payment(self, sale_id, total_amount):
        """
        Displays a QR code encoding the sale reference and amount for the
        customer to scan and pay. This does not verify or confirm payment
        was received — no payment gateway is integrated (see Section 5,
        Excluded from Scope).
        """
        return generate_payment_qr(sale_id, total_amount)

    def get_sale(self, sale_id):
        return self.sale_repo.find_by_id(sale_id)

    def search_history(self, sale_id=None, date=None, limit=50):
        return self.sale_repo.search_history(sale_id=sale_id, date=date, limit=limit)

    def list_sales_between(self, start_date, end_date):
        return self.sale_repo.list_between(start_date, end_date)

    def list_refunds_for_sale(self, sale_id):
        return self.refund_service.list_refunds_for_sale(sale_id)

    def list_refunds_between(self, start_date, end_date):
        return self.refund_service.list_refunds_between(start_date, end_date)

    def get_refund_form_data(self, sale_id):
        return self.refund_service.get_refund_form_data(sale_id)

    def refund_sale(self, sale_id, refund_lines, staff_id, reason=None):
        return self.refund_service.refund_sale(sale_id, refund_lines, staff_id, reason=reason)
