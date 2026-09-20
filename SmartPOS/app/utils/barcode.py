"""QR/barcode generation helpers.

Extracted from SalesService.generate_qr_payment (a pure function with no
side effects — same input always produces the same image), so it lives
alongside the other cross-cutting utilities instead of inside one
service. SalesService now just calls generate_qr_data_uri() below;
nothing about its behavior changed.
"""
import io
import base64
import qrcode


def generate_qr_data_uri(payload: str) -> str:
    """Encodes `payload` as a QR code PNG and returns it as a data: URI
    ready to drop straight into an <img src="..."> tag."""
    img = qrcode.make(payload)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def generate_payment_qr(sale_id, total_amount) -> str:
    """QR payload for the checkout "scan to pay" screen. Encodes the sale
    reference and amount only — there's no payment gateway integration,
    so this doesn't verify or confirm that payment was actually received."""
    payload = f"smartpos-pay:sale={sale_id}:amount={total_amount:.2f}"
    return generate_qr_data_uri(payload)
