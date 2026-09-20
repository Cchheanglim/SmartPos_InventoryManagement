"""Real WTForms validator for app/routes/inventory/category_routes.py."""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional, Length


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])
