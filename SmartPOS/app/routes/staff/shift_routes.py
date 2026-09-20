from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.utils.decorators import permission_required
from app.services.staff.shift_service import ShiftService

bp = Blueprint("shift", __name__)
shift_service = ShiftService()


@bp.route("/")
@login_required
@permission_required("manage_users")
def list_shifts():
    shifts = shift_service.list_shifts()
    return render_template("staff/shifts.html", shifts=shifts, editing=None)


@bp.route("/new", methods=["POST"])
@login_required
@permission_required("manage_users")
def create_shift():
    try:
        shift_service.create_shift(
            name=request.form.get("name", ""),
            start_time=request.form.get("start_time"),
            end_time=request.form.get("end_time"),
        )
        flash("Shift template created.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("shift.list_shifts"))


@bp.route("/<int:shift_id>/edit")
@login_required
@permission_required("manage_users")
def edit_shift(shift_id):
    shifts = shift_service.list_shifts()
    editing = shift_service.get_shift(shift_id)
    if editing is None:
        flash("Shift template not found.", "error")
        return redirect(url_for("shift.list_shifts"))
    return render_template("staff/shifts.html", shifts=shifts, editing=editing)


@bp.route("/<int:shift_id>/update", methods=["POST"])
@login_required
@permission_required("manage_users")
def update_shift(shift_id):
    try:
        shift_service.update_shift(
            shift_id,
            name=request.form.get("name", ""),
            start_time=request.form.get("start_time"),
            end_time=request.form.get("end_time"),
        )
        flash("Shift template updated.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("shift.list_shifts"))


@bp.route("/<int:shift_id>/delete", methods=["POST"])
@login_required
@permission_required("manage_users")
def delete_shift(shift_id):
    shift_service.delete_shift(shift_id)
    flash("Shift template deleted.", "success")
    return redirect(url_for("shift.list_shifts"))
