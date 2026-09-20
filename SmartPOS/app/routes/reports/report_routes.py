from flask import Blueprint, render_template, request, Response
from flask_login import login_required

from app.utils.decorators import permission_required
from app.services.reports.analytics_service import AnalyticsService
from app.services.sales.sales_service import SalesService
from app.services.reports.export_service import ExportService
from app.models.reports.report_filter import ReportFilter

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
analytics_service = AnalyticsService()
sales_service = SalesService()
export_service = ExportService()


def _parse_range(default_days=7):
    """Kept as a thin wrapper so existing callers below don't need to
    change — the actual date-parsing logic now lives in ReportFilter,
    shared with the export endpoints."""
    rf = ReportFilter.from_request_args(request.args, default_days)
    return rf.start, rf.end


@reports_bp.route("/")
@login_required
@permission_required("view_reports")
def index():
    """Business Dashboard — the main reporting landing page."""
    start, end = _parse_range()
    data = analytics_service.business_dashboard(start, end)
    return render_template("reports/business_dashboard.html", data=data)


@reports_bp.route("/business-health")
@login_required
@permission_required("view_reports")
def business_health():
    start, end = _parse_range()
    data = analytics_service.business_health(start, end)
    return render_template("reports/business_health.html", data=data)


@reports_bp.route("/crm")
@login_required
@permission_required("view_reports")
def crm_dashboard():
    start, end = _parse_range(default_days=30)
    data = analytics_service.crm_dashboard(start, end)
    return render_template("reports/crm_dashboard.html", data=data)


@reports_bp.route("/export/sales")
@login_required
@permission_required("view_reports")
def export_sales_csv():
    """Downloads every sale in the selected date range as a CSV."""
    rf = ReportFilter.from_request_args(request.args)
    csv_data = export_service.sales_csv(rf)
    return Response(
        csv_data, mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sales_{rf.label}.csv"},
    )


@reports_bp.route("/export/refunds")
@login_required
@permission_required("view_reports")
def export_refunds_csv():
    """Downloads every refund in the selected date range as a CSV."""
    rf = ReportFilter.from_request_args(request.args)
    csv_data = export_service.refunds_csv(rf)
    return Response(
        csv_data, mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=refunds_{rf.label}.csv"},
    )
