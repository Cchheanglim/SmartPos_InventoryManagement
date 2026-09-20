"""
Builds the CSV exports for the reports module. Extracted from
app/routes/reports/report_routes.py's export_sales_csv/export_refunds_csv
— same output, just moved out of the route so the route stays thin and
the CSV-building logic is testable without a Flask request context.
"""
from app.services.sales.sales_service import SalesService
from app.utils.csv_export import rows_to_csv_string


class ExportService:
    def __init__(self):
        self.sales_service = SalesService()

    def sales_csv(self, report_filter):
        sales = self.sales_service.list_sales_between(report_filter.start, report_filter.end)
        header = ["Sale ID", "Date", "Cashier", "Discount %", "Tax %", "Payment Method", "Total Amount"]
        rows = [
            [s.id, s.created_at, s.cashier_name, s.discount_percent, s.tax_percent, s.payment_method, s.total_amount]
            for s in sales
        ]
        return rows_to_csv_string(header, rows)

    def refunds_csv(self, report_filter):
        refunds = self.sales_service.list_refunds_between(report_filter.start, report_filter.end)
        header = ["Refund ID", "Sale ID", "Date", "Processed By", "Amount", "Reason"]
        rows = [
            [r.id, r.sale_id, r.created_at, r.processed_by_name, r.refund_amount, r.reason or ""]
            for r in refunds
        ]
        return rows_to_csv_string(header, rows)
