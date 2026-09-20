"""
Real WTForms validator for refunds (app/routes/sales/sales_routes.py,
sale_id/refund route).

Only `reason` is a fixed field — the actual quantities being refunded
come in as one dynamically-named field per sale line item
(`refund_qty_<sale_item_id>`, since a sale can have any number of line
items), which isn't expressible as a static WTForms field. Those are
validated where they're read, in SalesService.process_refund (each
quantity is checked against that line's remaining refundable_quantity).
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Optional, Length


class RefundForm(FlaskForm):
    reason = StringField("Reason", validators=[Optional(), Length(max=255)])
