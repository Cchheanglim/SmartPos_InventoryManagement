from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.utils.decorators import permission_required
from app.services.staff.task_service import TaskService
from app.services.auth.auth_service import AuthService
from app.repositories.auth.user_repository import UserRepository

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
task_service = TaskService()
auth_service = AuthService()
user_repo = UserRepository()


@tasks_bp.route("/")
@login_required
@permission_required("manage_users")
def list_tasks():
    """Admin-only view of every assigned task, across all staff."""
    tasks = task_service.all_tasks()
    staff = user_repo.list_all()
    return render_template("staff/tasks.html", tasks=tasks, staff=staff)


@tasks_bp.route("/new", methods=["POST"])
@login_required
@permission_required("manage_users")
def new_task():
    try:
        task_service.assign_task(
            title=request.form.get("title", ""),
            description=request.form.get("description", ""),
            assigned_to=int(request.form["assigned_to"]),
            assigned_by=current_user.id,
        )
        flash("Task assigned.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.route("/<int:task_id>/complete", methods=["POST"])
@login_required
def complete_task(task_id):
    """
    Any logged-in staff member can hit this — the service itself enforces
    that only the assigned person (or an Admin) can actually complete it.
    """
    can_manage_users = auth_service.has_permission(current_user, "manage_users")
    try:
        task_service.complete_task(task_id, current_user, can_manage_users)
        flash("Task marked complete.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(request.referrer or url_for("dashboard.index"))


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_users")
def delete_task(task_id):
    task_service.delete_task(task_id)
    flash("Task removed.", "info")
    return redirect(url_for("tasks.list_tasks"))
