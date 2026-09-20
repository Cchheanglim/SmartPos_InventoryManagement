"""Real WTForms validator for app/routes/staff/task_routes.py."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    assigned_to = SelectField("Assign To", coerce=int, validators=[DataRequired()])

    def __init__(self, *args, staff_choices=None, **kwargs):
        """staff_choices: list of (user_id, user_name) tuples from
        UserRepository.list_all(), fetched at request time."""
        super().__init__(*args, **kwargs)
        self.assigned_to.choices = staff_choices or []
