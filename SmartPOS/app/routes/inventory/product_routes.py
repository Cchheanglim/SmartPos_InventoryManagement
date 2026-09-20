import os
import io
import csv
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.utils.decorators import permission_required
from app.services.inventory.inventory_service import InventoryService
from app.services.inventory.category_service import CategoryService
from app.services.inventory.supplier_service import SupplierService

products_bp = Blueprint("products", __name__, url_prefix="/products")
inventory_service = InventoryService()
category_service = CategoryService()
supplier_service = SupplierService()


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def _save_uploaded_image(file_storage):
    """Saves an uploaded image with a unique filename, returns the stored filename or None."""
    if not file_storage or file_storage.filename == "":
        return None
    if not _allowed_file(file_storage.filename):
        raise ValueError("Image must be PNG, JPG, JPEG, GIF, or WEBP.")
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(unique_name)
    file_storage.save(os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name))
    return safe_name


@products_bp.route("/")
@login_required
@permission_required("manage_products")
def list_products():
    products = inventory_service.list_products()
    categories = inventory_service.list_categories()
    return render_template("products/list.html", products=products, categories=categories)


@products_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("manage_products")
def new_product():
    if request.method == "POST":
        try:
            image_filename = _save_uploaded_image(request.files.get("image"))
            inventory_service.create_product(
                name=request.form["name"].strip(),
                category=request.form.get("category", "").strip() or None,
                price=float(request.form["price"]),
                quantity_in_stock=int(request.form["quantity_in_stock"]),
                low_stock_threshold=int(request.form.get("low_stock_threshold") or 5),
                sku=request.form.get("sku", "").strip() or None,
                cost=float(request.form.get("cost") or 0),
                supplier_name=request.form.get("supplier_name", "").strip() or None,
                supplier_contact=request.form.get("supplier_contact", "").strip() or None,
                image_filename=image_filename,
            )
            flash("Product created.", "success")
            return redirect(url_for("products.list_products"))
        except (ValueError, KeyError) as e:
            flash(str(e), "error")
        except Exception:
            # e.g. duplicate SKU — MySQL raises IntegrityError, not ValueError
            flash("Could not create product — that SKU may already be in use by another product.", "error")
    suggested_sku = inventory_service.suggest_next_sku()
    return render_template(
        "products/form.html", product=None, suggested_sku=suggested_sku,
        categories=category_service.list_categories(), suppliers=supplier_service.list_suppliers(),
    )


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("manage_products")
def edit_product(product_id):
    product = inventory_service.get_product(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        try:
            # Only replace the image if a new file was actually uploaded;
            # otherwise keep the product's existing image.
            new_image = _save_uploaded_image(request.files.get("image"))
            image_filename = new_image if new_image else product.image_filename

            inventory_service.update_product(
                product_id=product_id,
                name=request.form["name"].strip(),
                category=request.form.get("category", "").strip() or None,
                price=float(request.form["price"]),
                low_stock_threshold=int(request.form.get("low_stock_threshold") or 5),
                sku=request.form.get("sku", "").strip() or None,
                cost=float(request.form.get("cost") or 0),
                supplier_name=request.form.get("supplier_name", "").strip() or None,
                supplier_contact=request.form.get("supplier_contact", "").strip() or None,
                image_filename=image_filename,
            )
            flash("Product updated.", "success")
            return redirect(url_for("products.list_products"))
        except (ValueError, KeyError) as e:
            flash(str(e), "error")
        except Exception:
            # e.g. duplicate SKU — MySQL raises IntegrityError, not ValueError
            flash("Could not save — that SKU may already be in use by another product.", "error")
    return render_template(
        "products/form.html", product=product, suggested_sku=None,
        categories=category_service.list_categories(), suppliers=supplier_service.list_suppliers(),
    )


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_products")
def delete_product(product_id):
    try:
        inventory_service.delete_product(product_id)
        flash("Product deleted.", "info")
    except Exception:
        # Products are referenced by sale_items, stock_movements, and
        # purchase_orders with no ON DELETE CASCADE (deliberately — losing
        # a product shouldn't erase historical sales/stock records), so
        # MySQL raises IntegrityError for any product that's ever been
        # sold, adjusted, or ordered instead of ValueError.
        flash("Can't delete this product — it has sales, stock, or purchase order history. "
              "Consider lowering its stock to 0 instead if you want to stop selling it.", "error")
    return redirect(url_for("products.list_products"))


@products_bp.route("/<int:product_id>/adjust-stock", methods=["POST"])
@login_required
@permission_required("adjust_stock")
def adjust_stock(product_id):
    try:
        change = int(request.form["change_amount"])
        reason = request.form.get("reason", "").strip() or "Manual adjustment"
        inventory_service.adjust_stock_manually(product_id, change, reason, staff_name=current_user.name)
        flash("Stock adjusted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("products.list_products"))


@products_bp.route("/<int:product_id>/barcode")
@login_required
@permission_required("manage_products")
def product_barcode(product_id):
    product = inventory_service.get_product(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.list_products"))
    return render_template("products/barcode.html", product=product)


@products_bp.route("/export")
@login_required
@permission_required("manage_products")
def export_products_csv():
    """Downloads the full product/inventory list as a CSV."""
    products = inventory_service.list_products()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["SKU", "Name", "Category", "Price", "Cost", "Quantity In Stock",
                      "Low Stock Threshold", "Supplier Name", "Supplier Contact"])
    for p in products:
        writer.writerow([p.sku or "", p.name, p.category or "", p.price, p.cost,
                          p.quantity_in_stock, p.low_stock_threshold,
                          p.supplier_name or "", p.supplier_contact or ""])
    return Response(
        buffer.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_export.csv"},
    )


# ---------- Purchase Orders / Restocking workflow ----------

@products_bp.route("/purchase-orders")
@login_required
@permission_required("adjust_stock")
def list_purchase_orders():
    status = request.args.get("status") or None
    orders = inventory_service.list_purchase_orders(status=status)
    received_total = sum(po.total_cost for po in orders if po.status == "received" and po.total_cost is not None)
    return render_template("products/purchase_orders.html", orders=orders, status=status, received_total=received_total)


@products_bp.route("/<int:product_id>/purchase-orders/new", methods=["GET", "POST"])
@login_required
@permission_required("adjust_stock")
def new_purchase_order(product_id):
    product = inventory_service.get_product(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        try:
            unit_cost_str = request.form.get("unit_cost", "").strip()
            inventory_service.create_purchase_order(
                product_id=product_id,
                quantity_ordered=int(request.form["quantity_ordered"]),
                staff_id=current_user.id,
                staff_name=current_user.name,
                unit_cost=float(unit_cost_str) if unit_cost_str else None,
                supplier_name=request.form.get("supplier_name", "").strip() or None,
                supplier_contact=request.form.get("supplier_contact", "").strip() or None,
                notes=request.form.get("notes", "").strip() or None,
            )
            flash("Purchase order created.", "success")
            return redirect(url_for("products.list_purchase_orders"))
        except (ValueError, KeyError) as e:
            flash(str(e), "error")
    return render_template("products/purchase_order_form.html", product=product)


@products_bp.route("/purchase-orders/<int:po_id>/receive", methods=["POST"])
@login_required
@permission_required("adjust_stock")
def receive_purchase_order(po_id):
    try:
        inventory_service.receive_purchase_order(po_id, current_user.id, staff_name=current_user.name)
        flash("Purchase order received — stock has been added.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("products.list_purchase_orders"))


@products_bp.route("/purchase-orders/<int:po_id>/cancel", methods=["POST"])
@login_required
@permission_required("adjust_stock")
def cancel_purchase_order(po_id):
    try:
        inventory_service.cancel_purchase_order(po_id)
        flash("Purchase order cancelled.", "info")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("products.list_purchase_orders"))
