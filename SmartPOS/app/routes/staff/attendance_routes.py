from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.utils.decorators import permission_required
from app.services.staff.attendance_service import AttendanceService

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")
attendance_service = AttendanceService()


@attendance_bp.route("/<int:attendance_id>/force-close", methods=["POST"])
@login_required
@permission_required("manage_users")
def force_close(attendance_id):
    try:
        attendance_service.admin_force_close(attendance_id)
        flash("Shift closed. No cash reconciliation was recorded for it.", "warning")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("attendance.attendance_log"))


@attendance_bp.route("/clock-in", methods=["POST"])
@login_required
def clock_in():
    starting_cash = request.form.get("starting_cash", "").strip()
    try:
        attendance_service.clock_in(current_user.id, starting_cash=float(starting_cash) if starting_cash else None)
        flash("Clocked in. Have a good shift!", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("dashboard.index"))


@attendance_bp.route("/clock-out", methods=["POST"])
@login_required
def clock_out():
    counted_cash = request.form.get("counted_cash", "").strip()
    try:
        shift = attendance_service.clock_out(
            current_user.id, counted_cash=float(counted_cash) if counted_cash else None
        )
        if shift.cash_difference is not None:
            diff = float(shift.cash_difference)
            if abs(diff) < 0.01:
                flash(f"Clocked out. Drawer matches exactly (expected ${shift.expected_cash:.2f}).", "success")
            elif diff > 0:
                flash(f"Clocked out. Drawer is ${diff:.2f} OVER (expected ${shift.expected_cash:.2f}, counted ${shift.counted_cash:.2f}).", "info")
            else:
                flash(f"Clocked out. Drawer is ${abs(diff):.2f} SHORT (expected ${shift.expected_cash:.2f}, counted ${shift.counted_cash:.2f}).", "error")
        else:
            flash("Clocked out. See you next shift!", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("dashboard.index"))


@attendance_bp.route("/log")
@login_required
@permission_required("manage_users")
def attendance_log():
    """Admin-only view of everyone's recent clock in/out activity."""
    records = attendance_service.recent_all(limit=100)
    return render_template("staff/attendance.html", records=records)
