"""
Assembles the home dashboard's data, extracted from
app/routes/dashboard/dashboard_routes.py's index() view — which
permission-gated sections a user sees (stock stats, today's shop-wide
totals, their own totals, recent sales, low stock, clock status, tasks)
was already real logic living in the route; this just gives it a proper
service-layer home so the route itself can stay thin.
"""
from app.services.inventory.inventory_service import InventoryService
from app.services.reports.report_service import ReportService
from app.services.staff.attendance_service import AttendanceService
from app.services.staff.task_service import TaskService


class DashboardService:
    def __init__(self):
        self.inventory_service = InventoryService()
        self.report_service = ReportService()
        self.attendance_service = AttendanceService()
        self.task_service = TaskService()

    def get_dashboard_data(self, user, permissions):
        stock_stats = None
        low_stock = []
        if "manage_products" in permissions or "adjust_stock" in permissions:
            all_products = self.inventory_service.list_products()
            low_stock = [p for p in all_products if p.is_low_stock]
            stock_stats = {
                "total_products": len(all_products),
                "low_stock_count": len(low_stock),
            }

        today_stats = None
        recent_sales = []
        if "view_reports" in permissions:
            today = self.report_service.today_summary()
            today_stats = {
                "num_sales": today["num_sales"],
                "revenue": float(today["total_revenue"]),
            }
            # Admin/Admin Assistant see the whole shop's latest activity.
            recent_sales = self.report_service.recent_sales(limit=5)

        my_stats = None
        if "process_sale" in permissions:
            mine = self.report_service.today_summary_for_cashier(user.id)
            my_stats = {
                "num_sales": mine["num_sales"],
                "revenue": float(mine["total_revenue"]),
            }
            # A Cashier only sees their own recent sales, not the whole shop's.
            if not recent_sales:
                recent_sales = self.report_service.recent_sales(limit=5, cashier_id=user.id)

        return {
            "stock_stats": stock_stats,
            "today_stats": today_stats,
            "my_stats": my_stats,
            "low_stock": low_stock[:5],
            "recent_sales": recent_sales,
            "clock_status": self.attendance_service.get_status(user.id),
            "my_tasks": self.task_service.tasks_for_user(user.id),
        }
