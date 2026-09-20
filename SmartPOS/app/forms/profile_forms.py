"""Real WTForms validators for app/routes/profile/profile_routes.py."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField
from wtforms.validators import Optional, DataRequired, EqualTo, Length


class ProfileForm(FlaskForm):
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    avatar = FileField("Profile Picture", validators=[Optional(), FileAllowed(
        ["jpg", "jpeg", "png", "gif", "webp"], "Images only.",
    )])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
