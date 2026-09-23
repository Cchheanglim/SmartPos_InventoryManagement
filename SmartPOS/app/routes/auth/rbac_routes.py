"""
RBAC Routes: Flask Blueprint for runtime Role and Permission management.
All endpoints are strictly protected by @login_required and @permission_required("manage_roles").
Controllers are thin and delegate all domain rules and safeguards to RBACService.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.utils.decorators import permission_required
from app.services.auth.rbac_service import RBACService
from app.repositories.auth.user_repository import UserRepository

rbac_bp = Blueprint("rbac", __name__, url_prefix="/rbac")
rbac_service = RBACService()
user_repo = UserRepository()


@rbac_bp.route("/", methods=["GET"])
@login_required
@permission_required("manage_roles")
def index():
    """
    Main RBAC control center displaying:
    1. Role management list (with user counts, rename, and delete safeguards)
    2. Permission management list (system vs custom permissions)
    3. Live Role x Permission checkbox security matrix
    4. User role quick assignment table
    """
    matrix_data = rbac_service.get_matrix_data()
    users = user_repo.list_all()

    return render_template(
        "auth/rbac.html",
        roles=matrix_data["roles"],
        all_permissions=matrix_data["all_permissions"],
        current=matrix_data["current"],
        manage_roles_id=matrix_data["manage_roles_id"],
        users=users,
    )


# -------------------------------------------------------------------------
# Role Routes
# -------------------------------------------------------------------------

@rbac_bp.route("/roles/new", methods=["POST"])
@login_required
@permission_required("manage_roles")
def create_role():
    role_name = request.form.get("name", "").strip()
    try:
        rbac_service.create_role(role_name)
        flash(f"Role '{role_name}' has been created successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to create role: {e}", "error")
    return redirect(url_for("rbac.index"))


@rbac_bp.route("/roles/<int:role_id>/edit", methods=["POST"])
@login_required
@permission_required("manage_roles")
def edit_role(role_id):
    new_name = request.form.get("name", "").strip()
    try:
        rbac_service.rename_role(role_id, new_name)
        flash("Role renamed successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to rename role: {e}", "error")
    return redirect(url_for("rbac.index"))


@rbac_bp.route("/roles/<int:role_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_roles")
def delete_role(role_id):
    try:
        rbac_service.delete_role(role_id)
        flash("Role has been deleted successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to delete role: {e}", "error")
    return redirect(url_for("rbac.index"))


# -------------------------------------------------------------------------
# Permission Routes
# -------------------------------------------------------------------------

@rbac_bp.route("/permissions/new", methods=["POST"])
@login_required
@permission_required("manage_roles")
def create_permission():
    perm_name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    try:
        rbac_service.create_permission(perm_name, description)
        flash(f"Permission '{perm_name}' has been created successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to create permission: {e}", "error")
    return redirect(url_for("rbac.index"))


@rbac_bp.route("/permissions/<int:permission_id>/edit", methods=["POST"])
@login_required
@permission_required("manage_roles")
def edit_permission(permission_id):
    new_name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    try:
        rbac_service.rename_permission(permission_id, new_name, description)
        flash("Permission updated successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to update permission: {e}", "error")
    return redirect(url_for("rbac.index"))


@rbac_bp.route("/permissions/<int:permission_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_roles")
def delete_permission(permission_id):
    try:
        rbac_service.delete_permission(permission_id)
        flash("Permission deleted successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to delete permission: {e}", "error")
    return redirect(url_for("rbac.index"))


# -------------------------------------------------------------------------
# Matrix Save Route
# -------------------------------------------------------------------------

@rbac_bp.route("/matrix", methods=["POST"])
@login_required
@permission_required("manage_roles")
def save_matrix():
    roles = rbac_service.list_roles()
    new_sets = {}
    for role in roles:
        selected_ids = {int(pid) for pid in request.form.getlist(f"role_{role.id}") if pid.isdigit()}
        new_sets[role.id] = selected_ids

    try:
        rbac_service.save_matrix(new_sets)
        flash("Role-Permission matrix saved successfully. Changes are now active system-wide.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to update permission matrix: {e}", "error")
    return redirect(url_for("rbac.index"))


# -------------------------------------------------------------------------
# User Role Assignment Route
# -------------------------------------------------------------------------

@rbac_bp.route("/users/assign", methods=["POST"])
@login_required
@permission_required("manage_roles")
def assign_user_role():
    try:
        user_id = int(request.form.get("user_id", 0))
        role_id = int(request.form.get("role_id", 0))
        rbac_service.assign_user_role(user_id, role_id, acting_user_id=current_user.id)
        flash("Staff member role assignment updated successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Failed to assign user role: {e}", "error")
    return redirect(url_for("rbac.index"))
