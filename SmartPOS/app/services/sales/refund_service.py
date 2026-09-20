"""
Owns refund business rules, extracted from SalesService (refund_sale,
get_refund_form_data, list_refunds_for_sale, list_refunds_between).
SalesService keeps the same four method names — nothing that calls them
(app/routes/sales/sales_routes.py, app/services/reports/export_service.py)
needed to change — and just delegates to this internally.

Still owned by the sales domain rather than fully independent, since a
refund only ever exists relative to a specific sale (needs the original
sale's items, discount, and tax to compute the right amount) — this
split is about giving refunds their own single responsibility, not
pretending they're unrelated to the sale they reverse.
"""
from app.repositories.inventory.product_repository import ProductRepository
from app.repositories.sales.sale_repository import SaleRepository
from app.repositories.sales.refund_repository import RefundRepository
from app.repositories.inventory.stock_repository import StockMovementRepository
from app.utils.telegram import TelegramService


class RefundService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.sale_repo = SaleRepository()
        self.refund_repo = RefundRepository()
        self.stock_repo = StockMovementRepository()
        self.telegram = TelegramService()

    def list_refunds_for_sale(self, sale_id):
        return self.refund_repo.list_refunds_for_sale(sale_id)

    def list_refunds_between(self, start_date, end_date):
        return self.refund_repo.list_refunds_between(start_date, end_date)

    def get_refund_form_data(self, sale_id):
        """Returns the sale with each item's already-refunded quantity
        filled in, so the refund form can show what's still refundable."""
        sale = self.sale_repo.find_by_id(sale_id)
        if sale is None:
            return None
        refunded = self.refund_repo.refunded_quantities_for_sale(sale_id)
        for item in sale.items:
            item.refunded_quantity = refunded.get(item.id, 0)
        return sale

    def refund_sale(self, sale_id, refund_lines, staff_id, reason=None):
        """
        refund_lines: list of dicts {sale_item_id, quantity} — the cashier
        picks which lines and how many of each to reverse, so a single
        wrong item doesn't force voiding the whole sale.

        Validates every line against what's actually left to refund
        BEFORE writing anything (same all-or-nothing approach as
        checkout()), restores stock for each refunded unit, and applies
        the same discount/tax the original sale used so the refunded
        amount matches what the customer actually paid for those items.
        """
        sale = self.sale_repo.find_by_id(sale_id)
        if sale is None:
            raise ValueError("Sale not found.")

        refund_lines = [line for line in refund_lines if int(line.get("quantity", 0)) > 0]
        if not refund_lines:
            raise ValueError("Select at least one item and quantity to refund.")

        already_refunded = self.refund_repo.refunded_quantities_for_sale(sale_id)
        items_by_id = {item.id: item for item in sale.items}

        validated_lines = []
        refund_subtotal = 0
        for line in refund_lines:
            sale_item_id = int(line["sale_item_id"])
            quantity = int(line["quantity"])
            item = items_by_id.get(sale_item_id)
            if item is None:
                raise ValueError("That item doesn't belong to this sale.")
            remaining = item.quantity - already_refunded.get(sale_item_id, 0)
            if quantity > remaining:
                raise ValueError(
                    f"Cannot refund {quantity} of '{item.product_name}' — only {remaining} left to refund."
                )
            validated_lines.append({
                "sale_item_id": sale_item_id,
                "product_id": item.product_id,
                "quantity": quantity,
                "product_name": item.product_name,
            })
            refund_subtotal += float(item.unit_price) * quantity

        # Same discount/tax the original sale applied, so a refund of
        # part of a discounted or taxed sale reverses the right amount.
        discounted = refund_subtotal * (1 - float(sale.discount_percent) / 100)
        refund_amount = round(discounted * (1 + float(sale.tax_percent) / 100), 2)

        refund_id = self.refund_repo.create_refund_with_items(
            sale_id=sale_id,
            processed_by=staff_id,
            reason=reason,
            refund_amount=refund_amount,
            items=[{"sale_item_id": l["sale_item_id"], "quantity": l["quantity"]} for l in validated_lines],
        )

        # Restore stock and log it exactly like any other stock movement.
        for line in validated_lines:
            self.product_repo.adjust_stock(line["product_id"], line["quantity"])
            self.stock_repo.create(
                line["product_id"], line["quantity"], reason=f"Refund: Sale #{sale_id}"
            )

        try:
            item_summary = ", ".join(f"{l['product_name']} (x{l['quantity']})" for l in validated_lines)
            self.telegram.notify_refund(sale_id, refund_amount, item_summary, reason)
        except Exception:
            pass  # A notification failure should never break a completed refund.

        return refund_id
