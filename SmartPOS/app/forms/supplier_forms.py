"""Real WTForms validator for app/routes/inventory/supplier_routes.py."""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional, Email, Length


class SupplierForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    contact_name = StringField("Contact Name", validators=[Optional(), Length(max=100)])
    phone = StringField("Phone", validators=[Optional(), Length(max=50)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=150)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
