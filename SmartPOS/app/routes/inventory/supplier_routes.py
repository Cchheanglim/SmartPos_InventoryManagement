from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.utils.decorators import permission_required
from app.services.inventory.supplier_service import SupplierService

bp = Blueprint("supplier", __name__)
supplier_service = SupplierService()


@bp.route("/")
@login_required
@permission_required("manage_products")
def list_suppliers():
    suppliers = supplier_service.list_suppliers()
    return render_template("inventory/suppliers.html", suppliers=suppliers, editing=None)


@bp.route("/new", methods=["POST"])
@login_required
@permission_required("manage_products")
def create_supplier():
    try:
        supplier_service.create_supplier(
            name=request.form.get("name", ""),
            contact_name=request.form.get("contact_name", "").strip() or None,
            phone=request.form.get("phone", "").strip() or None,
            email=request.form.get("email", "").strip() or None,
            address=request.form.get("address", "").strip() or None,
        )
        flash("Supplier added.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("supplier.list_suppliers"))


@bp.route("/<int:supplier_id>/edit")
@login_required
@permission_required("manage_products")
def edit_supplier(supplier_id):
    suppliers = supplier_service.list_suppliers()
    editing = supplier_service.get_supplier(supplier_id)
    if editing is None:
        flash("Supplier not found.", "error")
        return redirect(url_for("supplier.list_suppliers"))
    return render_template("inventory/suppliers.html", suppliers=suppliers, editing=editing)


@bp.route("/<int:supplier_id>/update", methods=["POST"])
@login_required
@permission_required("manage_products")
def update_supplier(supplier_id):
    try:
        supplier_service.update_supplier(
            supplier_id,
            name=request.form.get("name", ""),
            contact_name=request.form.get("contact_name", "").strip() or None,
            phone=request.form.get("phone", "").strip() or None,
            email=request.form.get("email", "").strip() or None,
            address=request.form.get("address", "").strip() or None,
        )
        flash("Supplier updated.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("supplier.list_suppliers"))


@bp.route("/<int:supplier_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_products")
def delete_supplier(supplier_id):
    supplier_service.delete_supplier(supplier_id)
    flash("Supplier deleted.", "success")
    return redirect(url_for("supplier.list_suppliers"))
