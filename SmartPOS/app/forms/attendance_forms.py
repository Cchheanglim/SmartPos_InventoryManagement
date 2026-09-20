"""Real WTForms validator for app/routes/staff/attendance_routes.py.

clock_in takes no fields at all (just a POST). clock_out takes the cash
drawer reconciliation amounts below."""
from flask_wtf import FlaskForm
from wtforms import FloatField
from wtforms.validators import Optional, NumberRange


class ClockOutForm(FlaskForm):
    starting_cash = FloatField("Starting Cash", validators=[Optional(), NumberRange(min=0)])
    counted_cash = FloatField("Counted Cash", validators=[Optional(), NumberRange(min=0)])
