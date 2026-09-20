from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from app.services.notifications.notification_service import NotificationService

bp = Blueprint("notification", __name__)
notification_service = NotificationService()


@bp.route("/")
@login_required
def list_notifications():
    show = request.args.get("show", "all")
    notifications = notification_service.list_for_user(
        current_user.id, unread_only=(show == "unread"),
    )
    return render_template("notifications/index.html", notifications=notifications, show=show)


@bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    notification_service.mark_read(notification_id, current_user.id)
    return redirect(request.referrer or url_for("notification.list_notifications"))


@bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    notification_service.mark_all_read(current_user.id)
    return redirect(request.referrer or url_for("notification.list_notifications"))
