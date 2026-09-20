"""
Real WTForms validators for the auth module, matching the fields and
rules app/routes/auth/auth_routes.py already enforces manually.

Not wired into the routes (see forms/README.md for why) — available for
whoever wants to switch a route over to form.validate_on_submit(), or
for writing form-level unit tests independent of Flask's request context.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=6, message="Must be at least 6 characters.")]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
