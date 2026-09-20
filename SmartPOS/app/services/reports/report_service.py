from app.repositories.sales.sale_repository import SaleRepository


class ReportService:
    """Aggregates sales data for the reporting page. Read-only — never mutates data."""

    def __init__(self):
        self.sale_repo = SaleRepository()

    def daily_totals(self, days=7):
        return self.sale_repo.daily_totals(days=days)

    def today_summary(self):
        return self.sale_repo.today_summary()

    def today_summary_for_cashier(self, cashier_id):
        return self.sale_repo.today_summary_for_cashier(cashier_id)

    def recent_sales(self, limit=5, cashier_id=None):
        return self.sale_repo.list_recent(limit=limit, cashier_id=cashier_id)

    def best_selling_products(self, limit=5):
        return self.sale_repo.best_selling_products(limit=limit)

    def summary(self, days=7):
        totals = self.daily_totals(days=days)
        revenue = sum(float(row["total_revenue"] or 0) for row in totals)
        num_sales = sum(row["num_sales"] for row in totals)
        return {
            "days": days,
            "total_revenue": round(revenue, 2),
            "total_sales": num_sales,
            "daily_totals": totals,
            "best_sellers": self.best_selling_products(),
        }
