"""Generic CSV-writing helper, extracted from the export routes in
app/routes/reports/report_routes.py (writing rows to an in-memory CSV
buffer was duplicated between the sales and refunds export endpoints)."""
import io
import csv


def rows_to_csv_string(header: list, rows: list) -> str:
    """rows: an iterable of iterables, one per CSV row (not header)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue()
