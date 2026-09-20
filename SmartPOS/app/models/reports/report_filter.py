"""
Value object for a report's date range, extracted from the
`_parse_range()` helper in app/routes/reports/report_routes.py — every
report/export endpoint takes the same `?start=YYYY-MM-DD&end=YYYY-MM-DD`
query params with the same fallback (last 7 days), so this centralizes
that instead of leaving it as a private function only report_routes.py
could reach.
"""
from datetime import date, datetime, timedelta


class ReportFilter:
    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end

    @classmethod
    def from_request_args(cls, args, default_days: int = 7):
        """args: a Flask `request.args`-like mapping with optional
        'start'/'end' keys in YYYY-MM-DD format."""
        start_str = args.get("start")
        end_str = args.get("end")
        if start_str and end_str:
            try:
                return cls(
                    datetime.strptime(start_str, "%Y-%m-%d").date(),
                    datetime.strptime(end_str, "%Y-%m-%d").date(),
                )
            except ValueError:
                pass
        end = date.today()
        start = end - timedelta(days=default_days - 1)
        return cls(start, end)

    @property
    def label(self):
        return f"{self.start}_to_{self.end}"
