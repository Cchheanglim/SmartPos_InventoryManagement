"""Real WTForms validators for app/routes/staff/staff_routes.py."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Optional, Email, Length


class NewStaffForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    role_name = SelectField("Role", validators=[DataRequired()])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])

    def __init__(self, *args, role_choices=None, **kwargs):
        """role_choices: list of role name strings from RoleRepository.list_all(),
        fetched at request time since roles are data, not fixed at code time."""
        super().__init__(*args, **kwargs)
        self.role_name.choices = [(r, r) for r in (role_choices or [])]


class EditStaffForm(FlaskForm):
    """Role + shift assignment (app/routes/staff/staff_routes.py, edit_staff)."""
    role_name = SelectField("Role", validators=[DataRequired()])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    shift_name = StringField("Shift Name", validators=[Optional(), Length(max=50)])
    shift_start = StringField("Shift Start", validators=[Optional()])  # HTML <input type="time">
    shift_end = StringField("Shift End", validators=[Optional()])

    def __init__(self, *args, role_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_name.choices = [(r, r) for r in (role_choices or [])]
