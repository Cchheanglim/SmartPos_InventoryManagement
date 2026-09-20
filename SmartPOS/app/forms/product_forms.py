"""Real WTForms validators for the product module, matching
app/routes/inventory/product_routes.py."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    sku = StringField("SKU", validators=[Optional(), Length(max=20)])
    category = StringField("Category", validators=[Optional(), Length(max=100)])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    quantity_in_stock = IntegerField("Quantity In Stock", validators=[DataRequired(), NumberRange(min=0)])
    low_stock_threshold = IntegerField("Low Stock Threshold", validators=[Optional(), NumberRange(min=0)], default=5)
    supplier_name = StringField("Supplier Name", validators=[Optional(), Length(max=150)])
    supplier_contact = StringField("Supplier Contact", validators=[Optional(), Length(max=100)])
    image = FileField("Product Image", validators=[Optional(), FileAllowed(
        ["jpg", "jpeg", "png", "gif", "webp"], "Images only.",
    )])


class StockAdjustmentForm(FlaskForm):
    change_amount = IntegerField(
        "Change Amount", validators=[DataRequired()],
        description="Positive to add stock, negative to remove it.",
    )
    reason = StringField("Reason", validators=[Optional(), Length(max=255)])
