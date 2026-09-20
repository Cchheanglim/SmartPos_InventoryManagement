from datetime import date, timedelta

from app.repositories.sales.sale_repository import SaleRepository
from app.repositories.sales.customer_repository import CustomerRepository
from app.repositories.inventory.product_repository import ProductRepository
from app.repositories.purchasing.purchase_order_repository import PurchaseOrderRepository


def _default_range(days=7):
    end = date.today()
    start = end - timedelta(days=days - 1)
    return start, end


class AnalyticsService:
    """
    Read-only aggregator behind the three reporting screens (Business
    Dashboard, Business Health, CRM Dashboard). Never mutates data — every
    method here is a SELECT-shaped query, composed from the repositories.
    """

    def __init__(self):
        self.sale_repo = SaleRepository()
        self.customer_repo = CustomerRepository()
        self.product_repo = ProductRepository()
        self.po_repo = PurchaseOrderRepository()

    # ---------- Business Dashboard ----------

    def business_dashboard(self, start_date=None, end_date=None):
        start, end = (start_date, end_date) if start_date and end_date else _default_range()
        revenue = self.sale_repo.revenue_between(start, end)
        low_stock_count = sum(1 for p in self.product_repo.list_all() if p.is_low_stock)

        return {
            "start": start,
            "end": end,
            "total_revenue": float(revenue["total_revenue"]),
            "total_sales": revenue["num_sales"],
            "total_orders": revenue["num_sales"],
            "estimated_profit": self._estimated_profit(start, end),
            "low_stock_count": low_stock_count,
            "revenue_trend": self.sale_repo.revenue_trend_between(start, end),
            "category_revenue": self.sale_repo.category_revenue_between(start, end),
            "payment_methods": self.sale_repo.payment_method_breakdown_between(start, end),
            "best_sellers": self.sale_repo.best_selling_products(limit=5),
            "lowest_sellers": self.sale_repo.lowest_selling_products(limit=5),
            "restock_intelligence": self.product_repo.restock_intelligence(),
        }

    def _estimated_profit(self, start, end):
        revenue = float(self.sale_repo.revenue_between(start, end)["total_revenue"])
        cogs = float(self.sale_repo.cost_of_goods_sold_between(start, end))
        return round(revenue - cogs, 2)

    # ---------- Business Health ----------

    def business_health(self, start_date=None, end_date=None):
        start, end = (start_date, end_date) if start_date and end_date else _default_range()
        revenue = float(self.sale_repo.revenue_between(start, end)["total_revenue"])
        expenses = float(self.sale_repo.cost_of_goods_sold_between(start, end))
        profit = round(revenue - expenses, 2)
        restocking_spend = self.po_repo.total_spent_between(start, end)

        return {
            "start": start,
            "end": end,
            "gross_revenue": round(revenue, 2),
            "total_expenses": round(expenses, 2),
            "net_profit": profit,
            "restocking_spend": round(restocking_spend, 2),
            "inventory_value": round(float(self.product_repo.total_inventory_value()), 2),
            "inventory_by_category": self.product_repo.inventory_value_by_category(),
            "daily_trend": self.sale_repo.daily_revenue_expense_profit_between(start, end),
            "expense_by_category": self.sale_repo.expense_by_category_between(start, end),
        }

    # ---------- CRM Dashboard ----------

    def crm_dashboard(self, start_date=None, end_date=None):
        start, end = (start_date, end_date) if start_date and end_date else _default_range(days=30)
        split = self.customer_repo.customer_vs_walkin_between(start, end)

        return {
            "start": start,
            "end": end,
            "total_customers": self.customer_repo.total_count(),
            "new_customers": self.customer_repo.new_customers_between(start, end),
            "sales_by_customer": self.customer_repo.sales_by_customer_between(start, end),
            "customer_orders": split["customer_orders"] or 0,
            "walkin_orders": split["walkin_orders"] or 0,
            "customer_revenue": float(split["customer_revenue"]),
            "walkin_revenue": float(split["walkin_revenue"]),
            "revenue_trend": self.sale_repo.revenue_trend_between(start, end),
        }
