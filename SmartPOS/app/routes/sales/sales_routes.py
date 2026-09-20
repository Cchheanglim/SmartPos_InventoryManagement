import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user

from app.utils.decorators import permission_required
from app.utils.receipt import format_receipt_text
from app.services.inventory.inventory_service import InventoryService
from app.services.sales.sales_service import SalesService, InsufficientStockError
from app.services.sales.crm_service import CRMService
from app.services.sales.held_order_service import HeldOrderService

sales_bp = Blueprint("sales", __name__, url_prefix="/checkout")
inventory_service = InventoryService()
sales_service = SalesService()
crm_service = CRMService()
held_order_service = HeldOrderService()


@sales_bp.route("/", methods=["GET"])
@login_required
@permission_required("process_sale")
def checkout_page():
    from flask import current_app
    products = inventory_service.list_products()
    categories = inventory_service.list_categories()
    return render_template(
        "sales/checkout.html", products=products, categories=categories,
        khr_rate=current_app.config["KHR_EXCHANGE_RATE"],
        default_tax_percent=current_app.config["DEFAULT_TAX_PERCENT"],
    )


@sales_bp.route("/customer-lookup")
@login_required
@permission_required("process_sale")
def customer_lookup():
    """AJAX endpoint the checkout page calls to show a masked tag before
    completing the sale, without ever sending the raw phone list around."""
    phone = request.args.get("phone", "")
    return jsonify(crm_service.lookup(phone))


@sales_bp.route("/submit", methods=["POST"])
@login_required
@permission_required("process_sale")
def submit_sale():
    try:
        cart = json.loads(request.form.get("cart_json", "[]"))
        discount_percent = float(request.form.get("discount_percent") or 0)
        tax_percent = float(request.form.get("tax_percent") or 0)
        payment_method = request.form.get("payment_method", "cash")
        customer_phone = request.form.get("customer_phone", "").strip() or None
        customer_name = request.form.get("customer_name", "").strip() or None

        sale = sales_service.checkout(
            cashier_id=current_user.id,
            cart_items=cart,
            discount_percent=discount_percent,
            tax_percent=tax_percent,
            payment_method=payment_method,
            customer_phone=customer_phone,
            customer_name=customer_name,
            cashier_name=current_user.name,
        )
        return redirect(url_for("sales.receipt", sale_id=sale.id))
    except InsufficientStockError as e:
        flash(str(e), "error")
        return redirect(url_for("sales.checkout_page"))
    except (ValueError, json.JSONDecodeError) as e:
        flash(f"Could not complete sale: {e}", "error")
        return redirect(url_for("sales.checkout_page"))


@sales_bp.route("/submit-async", methods=["POST"])
@login_required
@permission_required("process_sale")
def submit_sale_async():
    """Same checkout logic as /submit, but returns JSON so the checkout page
    can show the receipt as a modal instead of navigating to a new page."""
    try:
        payload = request.get_json(force=True)
        cart = payload.get("cart", [])
        discount_percent = float(payload.get("discount_percent") or 0)
        tax_percent = float(payload.get("tax_percent") or 0)
        payment_method = payload.get("payment_method", "cash")
        customer_phone = (payload.get("customer_phone") or "").strip() or None
        customer_name = (payload.get("customer_name") or "").strip() or None

        sale = sales_service.checkout(
            cashier_id=current_user.id,
            cart_items=cart,
            discount_percent=discount_percent,
            tax_percent=tax_percent,
            payment_method=payment_method,
            customer_phone=customer_phone,
            customer_name=customer_name,
            cashier_name=current_user.name,
        )

        masked_customer = None
        if sale.customer_phone:
            masked_customer = crm_service.masked_tag_for_phone(sale.customer_phone)

        qr_data_uri = None
        if sale.payment_method == "qr":
            qr_data_uri = sales_service.generate_qr_payment(sale.id, float(sale.total_amount))

        return jsonify({
            "success": True,
            "sale": {
                "id": sale.id,
                "created_at": str(sale.created_at),
                "cashier_name": sale.cashier_name,
                "discount_percent": float(sale.discount_percent),
                "tax_percent": float(sale.tax_percent),
                "payment_method": sale.payment_method,
                "total_amount": float(sale.total_amount),
                "masked_customer": masked_customer,
                "qr_data_uri": qr_data_uri,
                "items": [
                    {"name": i.product_name, "quantity": i.quantity, "unit_price": float(i.unit_price),
                     "line_total": float(i.line_total)}
                    for i in sale.items
                ],
            },
        })
    except InsufficientStockError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "message": f"Could not complete sale: {e}"}), 400


@sales_bp.route("/history")
@login_required
@permission_required("process_sale")
def sales_history():
    """Lets a cashier find a past sale — by exact ID, or by a specific
    date — to view or refund, since nothing else in the app links back
    to an old receipt."""
    search_id = request.args.get("sale_id", "").strip()
    search_date = request.args.get("date", "").strip()
    sale_id = int(search_id) if search_id.isdigit() else None
    sales = sales_service.search_history(sale_id=sale_id, date=search_date or None, limit=50)
    return render_template("sales/history.html", sales=sales, search_id=search_id, search_date=search_date)


@sales_bp.route("/<int:sale_id>/refund", methods=["GET", "POST"])
@login_required
@permission_required("process_refund")
def refund_sale(sale_id):
    sale = sales_service.get_refund_form_data(sale_id)
    if sale is None:
        flash("Sale not found.", "error")
        return redirect(url_for("sales.sales_history"))

    if request.method == "POST":
        refund_lines = []
        for item in sale.items:
            qty_str = request.form.get(f"refund_qty_{item.id}", "0").strip()
            if qty_str.isdigit() and int(qty_str) > 0:
                refund_lines.append({"sale_item_id": item.id, "quantity": int(qty_str)})
        reason = request.form.get("reason", "").strip() or None
        try:
            sales_service.refund_sale(sale_id, refund_lines, current_user.id, reason=reason)
            flash("Refund processed — stock has been restored.", "success")
            return redirect(url_for("sales.receipt", sale_id=sale_id))
        except ValueError as e:
            flash(str(e), "error")

    return render_template("sales/refund.html", sale=sale)


@sales_bp.route("/receipt/<int:sale_id>")
@login_required
@permission_required("process_sale")
def receipt(sale_id):
    sale = sales_service.get_sale(sale_id)
    if sale is None:
        flash("Sale not found.", "error")
        return redirect(url_for("sales.checkout_page"))

    qr_data_uri = None
    if sale.payment_method == "qr":
        qr_data_uri = sales_service.generate_qr_payment(sale.id, float(sale.total_amount))

    masked_customer = None
    if sale.customer_phone:
        masked_customer = crm_service.masked_tag_for_phone(sale.customer_phone)

    refunds = sales_service.list_refunds_for_sale(sale_id)

    return render_template(
        "sales/receipt.html", sale=sale, qr_data_uri=qr_data_uri,
        masked_customer=masked_customer, refunds=refunds,
    )


@sales_bp.route("/receipt/<int:sale_id>/download")
@login_required
@permission_required("process_sale")
def receipt_txt(sale_id):
    """Plain-text version of the receipt (see app/utils/receipt.py) —
    for printing on a receipt printer or saving a copy, alongside the
    on-screen HTML receipt above."""
    sale = sales_service.get_sale(sale_id)
    if sale is None:
        flash("Sale not found.", "error")
        return redirect(url_for("sales.checkout_page"))

    return Response(
        format_receipt_text(sale), mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename=receipt_{sale_id}.txt"},
    )


@sales_bp.route("/hold", methods=["POST"])
@login_required
@permission_required("process_sale")
def hold_order():
    payload = request.get_json(silent=True) or {}
    try:
        held_order_service.hold(
            cashier_id=current_user.id,
            cart_items=payload.get("cart", []),
            discount_percent=payload.get("discount_percent", 0),
            customer_phone=payload.get("customer_phone") or None,
            customer_name=payload.get("customer_name") or None,
            note=payload.get("note") or None,
        )
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@sales_bp.route("/held")
@login_required
@permission_required("process_sale")
def list_held_orders():
    orders = held_order_service.list_all()
    return jsonify({
        "orders": [
            {
                "id": o.id,
                "cashier_name": o.cashier_name,
                "held_at": o.held_at.strftime("%b %d, %I:%M %p") if o.held_at else "",
                "item_count": o.item_count,
                "estimated_total": o.estimated_total,
                "customer_phone": o.customer_phone,
                "customer_name": o.customer_name,
            }
            for o in orders
        ]
    })


@sales_bp.route("/held/<int:held_order_id>/resume", methods=["POST"])
@login_required
@permission_required("process_sale")
def resume_held_order(held_order_id):
    try:
        order = held_order_service.resume(held_order_id)
        return jsonify({
            "success": True,
            "cart": order.cart_items,
            "discount_percent": float(order.discount_percent),
            "customer_phone": order.customer_phone,
            "customer_name": order.customer_name,
        })
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@sales_bp.route("/held/<int:held_order_id>/discard", methods=["POST"])
@login_required
@permission_required("process_sale")
def discard_held_order(held_order_id):
    try:
        held_order_service.discard(held_order_id)
        return jsonify({"success": True})
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 404
