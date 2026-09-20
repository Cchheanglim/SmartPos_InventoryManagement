"""Real WTForms validator for the inline customer capture at checkout
(app/routes/sales/sales_routes.py — there's no separate customer
create/edit page; customer records are created automatically from
phone + name entered during checkout, per the CRM masking design)."""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Optional, Length


class CustomerLookupForm(FlaskForm):
    customer_phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    customer_name = StringField("Name", validators=[Optional(), Length(max=100)])
