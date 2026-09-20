"""
Formats a Sale as a plain-text receipt — the width (32 chars) matches a
standard thermal receipt printer, so this is usable for actual printing,
not just a downloadable .txt file. The existing receipt page
(app/templates/sales/receipt.html) is the on-screen HTML version; this
is the plain-text equivalent, used by the "download as .txt" route in
app/routes/sales/sales_routes.py (receipt_txt).
"""

WIDTH = 32


def _line(char="-"):
    return char * WIDTH


def _wrap_row(left, right):
    """Right-aligns `right` against `left` within WIDTH, e.g. "Cheetos x2 ... $8.00"."""
    space = WIDTH - len(left) - len(right)
    if space < 1:
        return f"{left}\n{' ' * (WIDTH - len(right))}{right}"
    return f"{left}{' ' * space}{right}"


def format_receipt_text(sale) -> str:
    lines = []
    lines.append("SmartPOS".center(WIDTH))
    lines.append(_line("="))
    lines.append(f"Sale #{sale.id}")
    lines.append(str(sale.created_at))
    lines.append(f"Cashier: {sale.cashier_name or '-'}")
    lines.append(_line())

    for item in sale.items:
        name = item.product_name or f"Product #{item.product_id}"
        lines.append(f"{name}")
        lines.append(_wrap_row(
            f"  {item.quantity} x {float(item.unit_price):.2f}",
            f"{float(item.line_total):.2f}",
        ))

    lines.append(_line())
    if sale.discount_percent:
        lines.append(_wrap_row("Discount", f"{float(sale.discount_percent):.1f}%"))
    if sale.tax_percent:
        lines.append(_wrap_row("Tax", f"{float(sale.tax_percent):.1f}%"))
    lines.append(_wrap_row("TOTAL", f"${float(sale.total_amount):.2f}"))
    lines.append(_wrap_row("Payment", sale.payment_method.upper()))
    lines.append(_line("="))
    lines.append("Thank you!".center(WIDTH))

    return "\n".join(lines)
