from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.services.auth.auth_service import AuthService
from app.services.reports.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)
auth_service = AuthService()
dashboard_service = DashboardService()


@dashboard_bp.route("/")
@login_required
def index():
    permissions = auth_service.get_permissions_for_user(current_user)
    data = dashboard_service.get_dashboard_data(current_user, permissions)
    return render_template("dashboard.html", **data)
