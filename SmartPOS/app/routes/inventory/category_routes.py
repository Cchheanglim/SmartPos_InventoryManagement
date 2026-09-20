from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.utils.decorators import permission_required
from app.services.inventory.category_service import CategoryService, CategoryInUseError, ICON_CHOICES

bp = Blueprint("category", __name__)
category_service = CategoryService()


@bp.route("/")
@login_required
@permission_required("manage_products")
def list_categories():
    categories = category_service.list_categories()
    return render_template("inventory/categories.html", categories=categories, editing=None, icon_choices=ICON_CHOICES)


@bp.route("/new", methods=["POST"])
@login_required
@permission_required("manage_products")
def create_category():
    try:
        category_service.create_category(
            name=request.form.get("name", ""),
            description=request.form.get("description", "").strip() or None,
            icon=request.form.get("icon") or None,
        )
        flash("Category created.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("category.list_categories"))


@bp.route("/<int:category_id>/edit")
@login_required
@permission_required("manage_products")
def edit_category(category_id):
    categories = category_service.list_categories()
    editing = category_service.get_category(category_id)
    if editing is None:
        flash("Category not found.", "error")
        return redirect(url_for("category.list_categories"))
    return render_template("inventory/categories.html", categories=categories, editing=editing, icon_choices=ICON_CHOICES)


@bp.route("/<int:category_id>/update", methods=["POST"])
@login_required
@permission_required("manage_products")
def update_category(category_id):
    try:
        category_service.update_category(
            category_id,
            name=request.form.get("name", ""),
            description=request.form.get("description", "").strip() or None,
            icon=request.form.get("icon") or None,
        )
        flash("Category updated.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("category.list_categories"))


@bp.route("/<int:category_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_products")
def delete_category(category_id):
    try:
        category_service.delete_category(category_id)
        flash("Category deleted.", "success")
    except CategoryInUseError as e:
        flash(str(e), "error")
    return redirect(url_for("category.list_categories"))
