"""Real WTForms validator for the purchase-order routes in
app/routes/inventory/product_routes.py (new_purchase_order)."""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class PurchaseOrderForm(FlaskForm):
    quantity_ordered = IntegerField("Quantity Ordered", validators=[DataRequired(), NumberRange(min=1)])
    unit_cost = FloatField("Unit Cost", validators=[Optional(), NumberRange(min=0)])
    supplier_name = StringField("Supplier Name", validators=[Optional(), Length(max=150)])
    supplier_contact = StringField("Supplier Contact", validators=[Optional(), Length(max=100)])
    notes = StringField("Notes", validators=[Optional(), Length(max=255)])
