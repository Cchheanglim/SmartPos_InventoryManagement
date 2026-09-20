"""
Real WTForms validator for checkout (app/routes/sales/sales_routes.py).

The live checkout page (sales/checkout.html) submits via JSON fetch to
/checkout/submit-async, not a plain form post, so this validates the same
fields for the form-post fallback (/checkout/submit) and for anyone
wiring a server-rendered checkout form in the future. `cart` itself
(product_id/quantity pairs) is validated in SalesService, since its shape
is a JSON list rather than a flat form field.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import Optional, NumberRange, Length


class CheckoutForm(FlaskForm):
    discount_percent = FloatField("Discount %", validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    tax_percent = FloatField("Tax %", validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    payment_method = SelectField(
        "Payment Method", choices=[("cash", "Cash"), ("qr", "QR / Bank Transfer")], default="cash",
    )
    customer_phone = StringField("Customer Phone", validators=[Optional(), Length(max=30)])
    customer_name = StringField("Customer Name", validators=[Optional(), Length(max=100)])
