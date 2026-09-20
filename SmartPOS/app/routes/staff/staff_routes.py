import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.utils.decorators import permission_required
from app.repositories.auth.user_repository import UserRepository
from app.repositories.auth.role_repository import RoleRepository, PermissionRepository
from app.repositories.staff.task_repository import TaskRepository
from app.repositories.staff.attendance_repository import AttendanceRepository
from app.services.auth.auth_service import AuthService
from app.services.staff.attendance_service import AttendanceService
from app.services.staff.shift_service import ShiftService

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")
user_repo = UserRepository()
role_repo = RoleRepository()
permission_repo = PermissionRepository()
task_repo = TaskRepository()
attendance_repo = AttendanceRepository()
auth_service = AuthService()
attendance_service = AttendanceService()
shift_service = ShiftService()


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


@staff_bp.route("/permissions", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def permissions_matrix():
    """
    Lets an Admin decide what each role can do by checking/unchecking
    permissions directly — this is the actual source of truth (the
    role_permissions table), not something fixed in the Python code.
    """
    roles = role_repo.list_all()
    all_permissions = permission_repo.list_all()

    if request.method == "POST":
        admin_role = next((r for r in roles if r.name == "admin"), None)

        # Compute what each role's new permission set would be first, so we
        # can validate everything before writing anything.
        new_sets = {}
        for role in roles:
            selected_ids = {int(pid) for pid in request.form.getlist(f"role_{role.id}")}
            new_sets[role.id] = selected_ids

        # The admin's "manage_users" checkbox is rendered disabled (locked
        # on) so it never appears in the submitted form data — force it
        # back in here rather than treating its absence as a real removal.
        manage_users_perm = next((p for p in all_permissions if p.name == "manage_users"), None)
        if admin_role and manage_users_perm:
            new_sets[admin_role.id].add(manage_users_perm.id)

        for role_id, permission_ids in new_sets.items():
            permission_repo.set_role_permissions(role_id, permission_ids)
        flash("Permissions updated.", "success")
        return redirect(url_for("staff.permissions_matrix"))

    current = {role.id: permission_repo.list_permission_ids_for_role(role.id) for role in roles}
    return render_template(
        "staff/permissions.html", roles=roles, all_permissions=all_permissions, current=current,
    )


@staff_bp.route("/")
@login_required
@permission_required("manage_users")
def list_staff():
    staff = user_repo.list_all()
    clocked_in_ids = attendance_service.currently_clocked_in_user_ids()
    return render_template("staff/list.html", staff=staff, clocked_in_ids=clocked_in_ids)


@staff_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def new_staff():
    roles = role_repo.list_all()
    if request.method == "POST":
        try:
            new_user_id = auth_service.register_user(
                name=request.form["name"].strip(),
                email=request.form["email"].strip(),
                password=request.form["password"],
                role_name=request.form["role_name"],
                phone=request.form.get("phone", "").strip(),
            )

            file_storage = request.files.get("avatar")
            if file_storage and file_storage.filename:
                if _allowed_file(file_storage.filename):
                    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
                    safe_name = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                    file_storage.save(os.path.join(current_app.config["AVATAR_UPLOAD_FOLDER"], safe_name))
                    user_repo.update_profile_picture(new_user_id, safe_name)
                else:
                    flash("Account created, but the photo wasn't a supported image type (PNG/JPG/GIF/WEBP) — add one later from Edit.", "warning")

            flash("Staff account created.", "success")
            return redirect(url_for("staff.list_staff"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception:
            # e.g. duplicate email — MySQL raises IntegrityError, not ValueError
            flash("Could not create account — that email or phone number may already be in use.", "error")
    return render_template("staff/form.html", roles=roles)


@staff_bp.route("/<int:user_id>")
@login_required
@permission_required("manage_users")
def view_staff(user_id):
    target = user_repo.find_by_id(user_id)
    if target is None:
        flash("Staff member not found.", "error")
        return redirect(url_for("staff.list_staff"))

    tasks = task_repo.list_for_user(user_id)
    tasks_completed = sum(1 for t in tasks if t.is_completed)
    attendance_sessions = attendance_repo.list_for_user(user_id, limit=1000)

    return render_template(
        "staff/details.html", staff_member=target,
        tasks_total=len(tasks), tasks_completed=tasks_completed,
        attendance_count=len(attendance_sessions),
        clocked_in=attendance_service.get_status(user_id) is not None,
    )


@staff_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def edit_staff(user_id):
    target = user_repo.find_by_id(user_id)
    if target is None:
        flash("Staff member not found.", "error")
        return redirect(url_for("staff.list_staff"))

    roles = role_repo.list_all()
    if request.method == "POST":
        new_role_name = request.form["role_name"]
        if user_id == current_user.id and new_role_name != "admin":
            flash("You can't change your own role away from Admin.", "error")
            return redirect(url_for("staff.list_staff"))

        role = role_repo.find_by_name(new_role_name)
        if role is None:
            flash("Unknown role selected.", "error")
            return render_template("staff/edit.html", staff_member=target, roles=roles, shift_templates=shift_service.list_shifts())

        try:
            user_repo.update_role(user_id, role.id)

            name = request.form.get("name", "").strip()
            if name and name != target.name:
                user_repo.update_name(user_id, name)

            email = request.form.get("email", "").strip()
            if email and email != target.email:
                user_repo.update_email(user_id, email)

            phone = request.form.get("phone", "").strip()
            user_repo.update_phone(user_id, re.sub(r"\D", "", phone) or None)

            shift_name = request.form.get("shift_name", "").strip() or None
            shift_start = request.form.get("shift_start", "").strip() or None
            shift_end = request.form.get("shift_end", "").strip() or None
            user_repo.set_shift(user_id, shift_name, shift_start, shift_end)

            flash(f"{name or target.name}'s details have been updated.", "success")
            return redirect(url_for("staff.list_staff"))
        except Exception:
            # e.g. that email or phone number is already used by another
            # account — MySQL raises IntegrityError, not ValueError
            flash("Could not save — that email or phone number may already be in use by another account.", "error")
            return render_template("staff/edit.html", staff_member=target, roles=roles, shift_templates=shift_service.list_shifts())

    return render_template("staff/edit.html", staff_member=target, roles=roles, shift_templates=shift_service.list_shifts())


@staff_bp.route("/<int:user_id>/permissions", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def user_permissions(user_id):
    """
    Lets an Admin grant a specific, trusted person extra permissions on
    top of whatever their role already allows — a targeted exception,
    not a role-wide change.
    """
    target = user_repo.find_by_id(user_id)
    if target is None:
        flash("Staff member not found.", "error")
        return redirect(url_for("staff.list_staff"))

    all_permissions = permission_repo.list_all()
    role_permission_ids = {
        p.id for p in all_permissions if p.name in permission_repo.list_for_role(target.role_id)
    }

    if request.method == "POST":
        selected_ids = {int(pid) for pid in request.form.getlist("extra_permissions")}
        # A role-given permission is never something to "grant" individually —
        # only permissions beyond the role count as an extra grant.
        extra_only = selected_ids - role_permission_ids
        permission_repo.set_user_permissions(user_id, extra_only, granted_by=current_user.id)
        flash(f"Updated {target.name}'s individual permissions.", "success")
        return redirect(url_for("staff.list_staff"))

    current_extra_ids = permission_repo.list_extra_permission_ids_for_user(user_id)
    return render_template(
        "staff/user_permissions.html",
        staff_member=target,
        all_permissions=all_permissions,
        role_permission_ids=role_permission_ids,
        current_extra_ids=current_extra_ids,
    )


@staff_bp.route("/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@permission_required("manage_users")
def toggle_active(user_id):
    if user_id == current_user.id:
        flash("You can't deactivate your own account.", "error")
        return redirect(url_for("staff.list_staff"))

    target = user_repo.find_by_id(user_id)
    if target is None:
        flash("Staff member not found.", "error")
        return redirect(url_for("staff.list_staff"))

    user_repo.set_active(user_id, not target.is_active)
    flash(f"{target.name} is now {'active' if not target.is_active else 'inactive'}.", "success")
    return redirect(url_for("staff.list_staff"))
